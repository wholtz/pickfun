import nox

py_versions = ['3.8', '3.9']


@nox.session
def flake8(session):
    session.run('poetry', 'install', external=True)
    session.run('flake8', 'pickfun', 'tests')


@nox.session
def black(session):
    session.run('poetry', 'install', external=True)
    session.run('black', '--check', '--diff', '--color', 'pickfun', 'tests')


@nox.session(python=py_versions)
def pylint(session):
    session.run('poetry', 'install', external=True)
    session.run('pylint', 'pickfun')


@nox.session(python=py_versions)
def mypy(session):
    session.run('poetry', 'install', external=True)
    session.run('mypy', 'pickfun', 'tests')


@nox.session(python=py_versions)
def test(session):
    session.run('poetry', 'install', external=True)
    session.run('pytest', '--cov', 'pickfun')
