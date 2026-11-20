# What: runs the report renderer through the documented command.
# Why: prevent an older generator from overwriting the current report.
# Viva: saved aggregate tables supply the report; no test records are scored.
from write_project_report import main


if __name__ == '__main__':
    main()
