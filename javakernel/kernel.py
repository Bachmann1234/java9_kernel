from subprocess import check_output
import signal
metakernel = False
try:
    from metakernel import MetaKernel as Kernel
    metakernel = True
except:
    try:
        from ipykernel.kernelbase import Kernel
    except ImportError:
        from IPython.kernel.zmq.kernelbase import Kernel
import os
import re
from pexpect import replwrap, EOF


class JavaKernel(Kernel):
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
        self.env = {"JAVA_9_HOME": os.environ['JAVA_9_HOME'],
                    "KULLA_HOME": os.environ['KULLA_HOME']}
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
                u'jshell> ',
                None,
                continuation_prompt=u'   ...> '
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
        if metakernel:
            return super(JavaKernel, self).do_execute(code, silent, store_history, user_expressions, allow_stdin)
        else:
            return self._do_execute(code, silent)

    def _execute_java(self, code):
        """
        :param code:
            The code to be executed.
        :return:
            interrupted and output
        """
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
        return interrupted, output


    def do_execute_direct(self, code, silent=False):
        """
        :param code:
            The code to be executed.
        :param silent:
            Whether to display output.
        :return:
            Return value, or None

        MetaKernel code handler.
        """
        if not code.strip():
            return None

        interrupted, output = self._execute_java(code)
        exitcode = "|  Error:" in output

        # Look for a return value:
        retval = None
        for expr in [".*\|  Expression value is: ([^\n]*)", 
                     ".*\|  Variable [^\n]* of type [^\n]* has value ([^\n]*)"]:
            match = re.match(expr, output, re.MULTILINE | re.DOTALL)
            if match:
                sretval = match.groups()[0]
                try:
                    # Turn string into a Python value:
                    retval = eval(sretval)
                except:
                    retval = sretval
                break

        if not silent:
            if exitcode:
                self.Error(output)
            else:
                print(output)
        return retval

    def _do_execute(self, code, silent):
        """
        :param code:
            The code to be executed.
        :param silent:
            Whether to display output.
        :return:
            Return value, or None

        Non-metakernel code handler. Need to construct all messages.
        """
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}

        interrupted, output = self._execute_java(code)

        if not silent:
            stream_content = {'name': 'stdout', 'text': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        if interrupted:
            return {'status': 'abort', 'execution_count': self.execution_count}

        exitcode = "|  Error:" in output

        if exitcode:
            return {'status': 'error', 'execution_count': self.execution_count,
                    'ename': '', 'evalue': output, 'traceback': []}
        else:
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}


    def get_completions(self, info):
        """
        Get command-line completions (TAB) from JShell:

        /vars
        |    Test test = Test@1c2c22f3
        
        /methods
        |    printf (Ljava/lang/String;[Ljava/lang/Object;)V
        |    draw ()V
        
        /classes
        |    class Test

        """
        token = info["help_obj"]
        matches = []
        for command, parts, part, text in [("/vars", 3, 1, ""),
                                           ("/methods", 2, 0, "()"),
                                           ("/classes", 2, 1, "()")]:
            interrupt, output = self._execute_java(command)
            for line in output.split("\n"):
                if len(line) > 1 and line[0] == "|":
                    items = line[1:].strip().split(" ", parts)
                    if items[part].startswith(token):
                        matches.append(items[part] + text)
        return matches
