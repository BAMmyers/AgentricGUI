# Plan to Fix Flake8 Errors

## For `app/utils.py`:
1. **Line Length Adjustments**: Shorten lines that exceed 79 characters by breaking them into multiple lines or rephrasing.
2. **Undefined Name**: Define the variable `blacklisted` in the `check_for_updates` function or remove its usage if it is not necessary.
3. **Blank Lines**: Ensure there are two blank lines between functions as per PEP 8 guidelines.

## For `app/main_window.py`:
1. **Line Length Adjustments**: Shorten lines that exceed 79 characters by breaking them into multiple lines or rephrasing.
2. **Indentation Fixes**: Correct the indentation for continuation lines to ensure they align properly with the previous line.

## Follow-Up Steps:
- After making the changes, run Flake8 again to ensure all issues are resolved.
- Verify the functionality of the application to ensure that no errors were introduced during the fixes.
