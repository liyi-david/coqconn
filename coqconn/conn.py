from os.path import join
from os import environ, read, write
from select import select

from .resp import parse_responses, ResponseParsingError

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

        AVOID to use this method directly if you do not want to retry
        connecting yourself. Use CoqConnection.connect instead.
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
            resps = self.read_until(lambda resps: resps[-1].is_feedback())
        except TimeoutError:
            self.proc.kill()
            raise TimeoutError

        self.timeout = timeout
        self.state_id = resps[-1].state_id


    def read_until(self, condition=lambda _:True):
        """
        the function reads a list of responses until a specified condition
        is satisfied.

        unfortunately, coq's xml protocol is not designed well enough, as a
        result, sometimes it is not trivial to figure out when we should stop
        reading. for example, when a coqtop instance is instalized and a new
        definition is added, the stop-reading condition is different.
        """
        data = ""
        resps = None

        while True:
            try:
                data += self.raw_read()
                print('RECV', data)
                resps = parse_responses(data)
                if condition(resps):
                    return resps
            except ResponseParsingError:
                pass


    def call(self, c):
        self.raw_write(c.to_string())

    def raw_write(self, s):
        print('SEND', s)
        _, prepared, _ = select([], [self.fin], [], self.timeout)
        if self.fin in prepared:
            write(self.fin, s)
        else:
            raise TimeoutError


    def raw_read(self):
        """
        the function performs synchronized read operation on the pipes of the
        coqtop process.
        """
        assert self.proc is not None, "read before connection is established!"
        prepared, _, _ = select([self.fout, self.ferr], [], [], self.timeout)

        if self.ferr in prepared:
            # FIXME into error mode
            # usually this error is caused by encoding problems, i.e. not because
            # of wrong coq commands
            raise CoqConnectionError(read(self.ferr, 0x4000).decode())
        elif self.fout in prepared:
            return read(self.fout, 0x4000).decode()
        else:
            raise TimeoutError


    def __repr__(self):
        return "coq_connection @ %s, %s" % (
                self.state_id,
                self.proc
                )
