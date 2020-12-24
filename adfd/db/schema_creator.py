import subprocess

from adfd.cnf import DB


def write_new_schema():
    content = subprocess.check_output(["sqlacodegen", DB.URL]).decode()
    with open("schema.py", "w") as f:
        f.write(content)


if __name__ == "__main__":
    # needs sqlacodegen installed
    write_new_schema()
