"""
code mostly from https://github.com/argoproj-labs/applicationset-hello-plugin
which is a template repo but has no license
revisions by @jessebot and those revisions are AGPL licensed
"""
from json import loads, dumps
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import yaml
import sys
from os import environ

ALL_LOGGING_LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
        }
LOG_LEVEL = environ.get("LOG_LEVEL", "warning").lower()

logging.basicConfig(stream=sys.stdout,
                    level=ALL_LOGGING_LEVELS[LOG_LEVEL],
                    format="%(asctime)s:%(levelname)s: %(message)s")

# token should be mounted as a volume at run time
with open("/var/run/argocd/token") as f:
    TOKEN = f.read().strip()

SECRET_VARS_FILE = environ.get("SECRET_VARS_FILE",
                               "/var/run/secret-plugin/secret_vars.yaml")

class Plugin(BaseHTTPRequestHandler):
    def __init__(self):
        self.secret_vars = {}

    def args(self):
        """
        this just gets the args requested, I thought
        """
        return loads(self.rfile.read(int(self.headers.get('Content-Length'))))

    def reply(self, reply):
        """
        return 200 HTTP code (success) if auth everything checks out
        """
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        # this is what actually gets sent to the argocd appset
        json_str = dumps(reply).encode("UTF-8")
        logging.debug(f"final reply phase: sending back json str: {json_str}")
        self.wfile.write(json_str)

    def forbidden(self):
        """
        return 403 HTTP (forbidden) code if authorization fails
        """
        self.send_response(403)
        self.end_headers()

    def unsupported(self):
        """
        return 404 HTTP code if we are asked for any other path than getparams
        """
        self.send_response(404)
        self.end_headers()

    def return_secret_vars(self, appset_name: str, secret_var_names: list):
        """
        Takes a list of string type keys in a secret to return
        """

        # returns list of dict like [{"secret_var": "secret_value"}]
        return_dict = {}

        logging.info(secret_var_names)

        # reload secrets file before checking
        self.reload_secret_vars()

        # iterate through requested secret keys
        for secret_var in secret_var_names:
            if secret_var not in self.secret_vars:
                msg = (f"'{secret_var}' not found in k8s secret, as requested by"
                       f" {appset_name}")
                logging.warning(msg)
            else:
                msg = (f"Found value for variable, '{secret_var}', as requested"
                       f" by {appset_name}")
                logging.info(msg)

                # creates a dict with the requested secret key name and value
                # then, appends it to the return_list
                return_dict[secret_var] = self.secret_vars[secret_var]

        return [return_dict]

    def reload_secret_vars(self):
        """
        reloads the secret vars file
        """
        with open(SECRET_VARS_FILE) as yaml_file:
            self.secret_vars = yaml.safe_load(yaml_file)

    def do_POST(self):
        args = self.args()
        appset_name = args['applicationSetName']

        # if the token is invalid, throw a forbidden error
        posted_auth = self.headers.get("Authorization")
        expected_auth = f"Bearer {TOKEN}"
        if posted_auth != expected_auth:
            err = (f"Recieved auth header from argo during {appset_name} request:"
                   f" '{posted_auth}' that does not match **REDACTED**")
            logging.error(err)
            self.forbidden()

        if self.path == '/api/v1/getparams.execute':
            try:
                secret_vars = args['input']['parameters']['secret_vars']
                return_params = self.return_secret_vars(appset_name, secret_vars)
            except Exception as e:
                err = f"{e}, We require input to run this plugin! We got {secret_vars}"
                logging.error(err)

            # reply with all variables requested
            reply_dictionary = {"output": {"parameters": return_params}}
            logging.info(f"replying to {appset_name} with {reply_dictionary}")
            self.reply(reply_dictionary)
        else:
            self.unsupported()


if __name__ == '__main__':
    httpd = HTTPServer(('', 4355), Plugin)
    httpd.serve_forever()
