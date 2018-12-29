from os.path import join
from os import environ, read
from select import select

import subprocess

def get_coq_version(coqtop):
    try:
        p = subprocess.Popen(
                [
                    coqtop,
                    '--version'
                    ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
                )

        (stdoutput, erroutput) = p.communicate()
        if erroutput != b"":
            print(erroutput)
            raise Exception
        else:
            version = stdoutput.decode().split("version ")[1].split(' ')[0]
            return version
    except:
        return None


class CoqConnectionError(Exception):
    pass


class CoqConnection:

    supported_versions = [ '8.7.1' ]

    @classmethod
    def connect(cls, coqtop=None, args=[], timeout=2):

        max_timeout_retries = 5
        for _ in range(max_timeout_retries):
            try:
                conn = CoqConnection(coqtop, args, timeout)
                return conn
            except TimeoutError:
                pass

    def __init__(self, coqtop=None, args=[], timeout=2):
        """
        A connection can be initialized with or without a coqtop command.
        If coqtop is None, we automatically detect the command under PATH.
        """
        version = None

        # STEP 1. check validity of coqtop

        if coqtop is not None:
            version = get_coq_version(coqtop)
        else:
            for path in environ['PATH'].split(':'):
                version = get_coq_version(join(path, 'coqtop'))
                if version is not None:
                    coqtop = join(path, 'coqtop')
                    break

        if version is None:
            raise CoqConnectionError(
                    'no coqtop found in $PATH!' if coqtop is None else '%s is not a valid coqtop executable!' % coqtop
                    )
        elif version not in self.supported_versions:
            raise CoqConnectionError("coqtop ver. %s is not supported, please consider installing %s" % (
                version,
                ' or '.join(self.supported_versions)
                )
            )

        # STEP 2. establish a connection
        full_args = [ coqtop, '-ideslave', '-main-channel', 'stdfds', '-async-proofs', 'on' ] + args
        self.proc = subprocess.Popen(full_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
                )

        self.fin = self.proc.stdin.fileno()
        self.fout = self.proc.stdout.fileno()
        self.ferr = self.proc.stderr.fileno()

        # FIXME
        # sometimes, coqtop just gets stuck when it is being initialized
        # currently we don't know why. such weird thing happens frequently
        # so we have to set up a strict timeout when initializing coq
        # connection. once we get no feedback, the connection is killed
        # and we restart it
        self.timeout = 0.2

        # STEP 3. wait until a FEEDBACK message comes
        try:
            self.waitfor_feedback()
        except TimeoutError:
            self.proc.kill()
            raise TimeoutError

        self.timeout = timeout


    def waitfor_feedback(self):
        print(self.raw_read())


    def raw_read(self):
        """
        the function performs synchronized read operation on the pipes of the
        coqtop process.
        """
        assert self.proc is not None, "read before connection is established!"
        prepared, _, _ = select([self.fout, self.ferr], [], [], self.timeout)

        if self.ferr in prepared:
            # into error mode
            # usually this error is caused by encoding problems, i.e. not because
            # of wrong coq commands
            pass
        elif self.fout in prepared:
            return read(self.fout, 0x4000)
        else:
            raise TimeoutError
