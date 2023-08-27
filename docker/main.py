"""
code mostly from https://github.com/argoproj-labs/applicationset-hello-plugin
which is a template repo but has no license
revisions by @jessebot and assumed to be whatever Argo's default license is
"""
from json import loads, dumps
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import yaml
import sys

logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s: %(message)s")

# token should be mounted as a volume at run time
with open("/var/run/argocd/token") as f:
    TOKEN = f.read().strip()

with open("/var/run/secret-plugin/secret_vars.yaml") as yaml_file:
    SECRET_VARS = yaml.safe_load(yaml_file)

class Plugin(BaseHTTPRequestHandler):

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
        self.end_headers()
        self.wfile.write(dumps(reply).encode("UTF-8"))

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

        # iterate through requested secret keys
        for secret_var in secret_var_names:
            if secret_var not in SECRET_VARS:
                msg = (f"'{secret_var}' not found in k8s secret, as requested by"
                       f" {appset_name}")
                logging.warning(msg)
            else:
                msg = (f"Found value for variable, '{secret_var}', as requested"
                       f" by {appset_name}")
                logging.info(msg)
                # creates a dict with the requested secret key name and value
                # then, appends it to the return_list
                return_dict[secret_var] = SECRET_VARS[secret_var]

        return [return_dict]

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
