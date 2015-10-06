from subprocess import check_output
import signal
try:
    from ipykernel.ipkernel import KernelBase
except ImportError:
    from IPython.kernel.zmq.kernelbase import Kernel
import os
from pexpect import replwrap, EOF


class JavaKernel(KernelBase):
    implementation = 'java_kernel'
    implementation_version = 0.1
    langauge = "java"
    language_version = "1.9.0-ea"
    language_info = {'name': 'java',
                     'mimetype': 'application/java-vm',
                     'file_extension': '.class'}

    _JAVA_COMMAND = '{}/bin/java'.format(os.environ['JAVA_9_HOME'])
    _KULLA_LOCATION = os.environ['KULLA_HOME']

    def __init__(self, **kwargs):
        super(JavaKernel, self).__init__(**kwargs)
        self._banner = None
        self._start_java_repl()

    @property
    def banner(self):
        if self._banner is None:
            self._banner = check_output([self._JAVA_COMMAND, '-version']).decode('utf-8')
        return self._banner

    def _start_java_repl(self):
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            self.javawrapper = replwrap.REPLWrapper(
                "{} -jar {}".format(
                    self._JAVA_COMMAND,
                    self._KULLA_LOCATION
                ),
                u'->',
                None
            )
        finally:
            signal.signal(signal.SIGINT, sig)

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        """
        :param code:
            The code to be executed.
        :param silent:
            Whether to display output.
        :param store_history:
            Whether to record this code in history and increase the execution count.
            If silent is True, this is implicitly False.
        :param user_expressions:
            Mapping of names to expressions to evaluate after the code has run. You can ignore this if you need to.
        :param allow_stdin:
            Whether the frontend can provide input on request
        :return:
            dict https://ipython.org/ipython-doc/dev/development/messaging.html#execution-results
        """
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}

        interrupted = False
        try:
            output = self.javawrapper.run_command(code.rstrip(), timeout=None)
        except KeyboardInterrupt:
            self.javawrapper.child.sendintr()
            interrupted = True
            self.javawrapper._expect_prompt()
            output = self.javawrapper.child.before
        except EOF:
            output = self.javawrapper.child.before + 'Restarting java'
            self._start_java_repl()

        if not silent:
            output = '\n'.join(output.split('\n')[1:])
            stream_content = {'name': 'stdout', 'text': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        if interrupted:
            return {'status': 'abort', 'execution_count': self.execution_count}

        exitcode = "|  Error: " in output

        if exitcode:
            return {'status': 'error', 'execution_count': self.execution_count,
                    'ename': '', 'evalue': output, 'traceback': []}
        else:
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=JavaKernel)
