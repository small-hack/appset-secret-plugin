"""
code mostly from https://github.com/argoproj-labs/applicationset-hello-plugin
which is a template repo but has no license
revisions by @jessebot and assumed to be whatever Argo's default license is
"""
from json import loads, dumps
from http.server import BaseHTTPRequestHandler, HTTPServer
from os import environ
import logging as log
import yaml

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

    def return_secret_vars(self, secret_var_names: list):
        """
        Takes a list of string type keys in a secret to return
        """

        # list of dictionaries to return like {"secret_var": "secret_value"}
        return_list = []

        log.info(secret_var_names)

        # iterate through requested secret keys
        for secret_var in secret_var_names:
            log.info("Argo CD Secret Plugin Generator recieved request for "
                     f"secret variable: {secret_var}")

            if secret_var not in SECRET_VARS:
                log.warning(f"Variable, '{secret_var}' does not exist")
            else:
                # creates a dict with the requested secret key name and value
                # then, appends it to the return_list
                return_list.append({secret_var: SECRET_VARS[secret_var]})

        return return_list

    def do_POST(self):
        # if the token is invalid, throw a forbidden error
        if self.headers.get("Authorization") != "Bearer " + TOKEN:
            self.forbidden()

        if self.path == '/api/v1/getparams.execute':
            args = self.args()

            try:
                secret_vars = args['input']['parameters']['secret_vars']
                return_params = self.return_secret_vars(secret_vars)
            except Exception as e:
                log.error(f"{e}, We require input to run this plugin! We got"
                          f"{secret_vars}")

            # reply with all variables requested
            reply_dictionary = {"output": {"parameters": return_params}}
            self.reply(reply_dictionary)
        else:
            self.unsupported()


if __name__ == '__main__':
    httpd = HTTPServer(('', 4355), Plugin)
    httpd.serve_forever()
