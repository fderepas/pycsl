# run #8 u55 witness 10225 (review rt66 g09): a benign local `apport` package. Ubuntu's
# stdlib-dir sitecustomize installs apport_python_hook, whose excepthook runs `import apport.report`
# from sys.path on an uncaught exception.
print("LOCAL apport package loaded:", __file__)
