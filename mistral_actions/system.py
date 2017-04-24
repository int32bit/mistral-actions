from mistral.actions.base import Action as action_base
import shlex
import subprocess


class Exec(action_base):
    """Run command with arguments and return its output as a byte string.

    :param cmd: the command to run, note you can use at most one pipe,
                like 'ls -l | wc -l'.
    """
    __export__ = True

    def __init__(self, cmd):
        self.commands = cmd.split('|')
        if len(self.commands) > 2:
            raise NotImplementedError("Not support for more than one pipes!")

    def run(self):
        if len(self.commands) == 1:
            output = subprocess.check_output(shlex.split(self.commands[0]))
        elif len(self.commands) == 2:
            # check the first command output because use pipe may ignore error
            subprocess.check_output(shlex.split(self.commands[0]))
            p1 = subprocess.Popen(
                shlex.split(self.commands[0]), stdout=subprocess.PIPE)
            p2 = subprocess.Popen(
                shlex.split(self.commands[1]),
                stdin=p1.stdout,
                stdout=subprocess.PIPE)
            p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
            output = p2.communicate()[0]
            if p1.returncode:
                raise subprocess.CalledProcessError(p1.returncode,
                                                    self.commands[0])
            if p2.returncode:
                raise subprocess.CalledProcessError(p2.returncode,
                                                    self.commands[1])
        else:
            raise NotImplementedError("Not support for more than one pipes!")
        return output
