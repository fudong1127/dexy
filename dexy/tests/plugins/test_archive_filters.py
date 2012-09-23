from dexy.doc import Doc
from dexy.tests.utils import wrap
import os
import tarfile
import zipfile

def test_zip_archive_filter():
    with wrap() as wrapper:
        with open("hello.py", "w") as f:
            f.write("print 'hello'")

        with open("hello.rb", "w") as f:
            f.write("puts 'hello'")

        doc = Doc("archive.zip|zip",
                Doc("hello.py", wrapper=wrapper),
                Doc("hello.rb", wrapper=wrapper),
                Doc("hello.py|pyg", wrapper=wrapper),
                Doc("hello.rb|pyg", wrapper=wrapper),
                contents=" ",
                wrapper=wrapper)

        wrapper.docs = [doc]
        wrapper.run()
        wrapper.report()

        assert os.path.exists("output/archive.zip")
        with zipfile.ZipFile("output/archive.zip", "r") as z:
            names = z.namelist()
            assert "archive/hello.py" in names
            assert "archive/hello.rb" in names
            assert "archive/hello.py-pyg.html" in names
            assert "archive/hello.rb-pyg.html" in names

def test_archive_filter():
    with wrap() as wrapper:
        with open("hello.py", "w") as f:
            f.write("print 'hello'")

        with open("hello.rb", "w") as f:
            f.write("puts 'hello'")

        doc = Doc("archive.tgz|archive",
                Doc("hello.py", wrapper=wrapper),
                Doc("hello.rb", wrapper=wrapper),
                Doc("hello.py|pyg", wrapper=wrapper),
                Doc("hello.rb|pyg", wrapper=wrapper),
                contents=" ",
                wrapper=wrapper)

        wrapper.docs = [doc]
        wrapper.run()
        wrapper.report()

        assert os.path.exists("output/archive.tgz")
        with tarfile.open("output/archive.tgz", mode="r:gz") as tar:
            names = tar.getnames()
            assert "archive/hello.py" in names
            assert "archive/hello.rb" in names
            assert "archive/hello.py-pyg.html" in names
            assert "archive/hello.rb-pyg.html" in names

def test_archive_filter_with_short_names():
    with wrap() as wrapper:
        with open("hello.py", "w") as f:
            f.write("print 'hello'")

        with open("hello.rb", "w") as f:
            f.write("puts 'hello'")

        doc = Doc("archive.tgz|archive",
                Doc("hello.py", wrapper=wrapper),
                Doc("hello.rb", wrapper=wrapper),
                Doc("hello.py|pyg", wrapper=wrapper),
                Doc("hello.rb|pyg", wrapper=wrapper),
                contents=" ",
                archive={'use-short-names' : True},
                wrapper=wrapper)

        wrapper.docs = [doc]
        wrapper.run()
        wrapper.report()

        assert os.path.exists("output/archive.tgz")
        with tarfile.open("output/archive.tgz", mode="r:gz") as tar:
            names = tar.getnames()
            assert "archive/hello.py" in names
            assert "archive/hello.rb" in names
            assert "archive/hello.html" in names

def test_unprocessed_directory_archive_filter():
    with wrap() as wrapper:
        with open("abc.txt", "w") as f:
            f.write('this is abc')

        with open("def.txt", "w") as f:
            f.write('this is def')

        doc = Doc("archive.tgz|tgzdir", contents="ignore", tgzdir={'dir' : '.'}, wrapper=wrapper)
        wrapper.docs = [doc]
        wrapper.run()
        wrapper.report()

        assert os.path.exists("output/archive.tgz")
        with tarfile.open("output/archive.tgz", mode="r:gz") as tar:
            names = tar.getnames()
            assert "./abc.txt" in names
            assert "./def.txt" in names