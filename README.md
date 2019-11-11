# CountHours

Python scripts to assist in hour accounting, for invoicing hourly based works.
You register the work done in a regular Markdown text file, respecting some formats to register the worked hours.
The script will count the worked hours and creates a summary with the totals hours grouped by month at the end of the log file.

## The markdown log file

A sample Markdown text file:

```markdown
# To do:

- Some pending tasks


# Actions:

## Date: 2014-02-10

Hours: ? {18:43-18:46 + 21:41-22:25}
- Check and tag
- Export and upload

## Date: 2014-01-20

Hours: ? {17:10-19:30}
- Editing video
- Sound normalization
- Color grading

## Date: 2014-01-17

Hours: 0:38:00 [0.63 h] {16:18-16:38 + 16:41-16:59 - 19:00-19:20}
- Watermark with logo
- Credits


# Summary:
- 2014-01 = 0.63 h
```

You register the work writing anywhere into the text files.
The worked hours are registered in two different line types:

- The Date line: `## Date: 2014-02-10`
- The worked hours line:
    - `Hours: ? {18:43-18:46}`
    - `Hours: ? {18:43-18:46 + 21:41-22:25}`
    - You can register many different periods on the same date
    - You can create more than one entry for a single day, as you prefer

Anywhere else on the file you have room for free text, in the example to register the actions we will write:

```markdown
## Date: 2014-02-10

Hours: ? {18:43-18:46 + 21:41-22:25}
- Check and tag
- Export and upload
```

Once processed the file, the question mark `?` will be replaced with the computed hours, like this:

```markdown
## Date: 2014-02-10

Hours: 0:47:00 [0.78 h] {18:43-18:46 + 21:41-22:25}
- Check and tag
- Export and upload
```

And the summary will be updated. The previous example file will be transformed into this one:

```markdown
# To do:

- Some pending tasks


# Actions:

## Date: 2014-02-10

Hours: 0:47:00 [0.78 h] {18:43-18:46 + 21:41-22:25}
- Check and tag
- Export and upload

## Date: 2014-01-20

Hours: 2:20:00 [2.33 h] {17:10-19:30}
- Editing video
- Sound normalization
- Color grading

## Date: 2014-01-17

Hours: 0:38:00 [0.63 h] {16:18-16:38 + 16:41-16:59 - 19:00-19:20}
- Watermark with logo
- Credits


# Summary:
- 2014-02 = 0.78 h
- 2014-01 = 2.96 h
```

Once computed the hours, you can write again onto the same file to register more work.

## Usage

Run the script `count_hours.py` with the following options:

```shell script
$ ./count_hours.py --help
usage: count_hours.py [-h] [-bf BACKUP_FOLDER] [-d] file_path

positional arguments:
  file_path             The Markdown file to process

optional arguments:
  -h, --help            show this help message and exit
  -bf BACKUP_FOLDER, --backup_folder BACKUP_FOLDER
                        Folder to store the backups
  -d, --debug           Shows all the DEBUG level logging messages
```

A backup copy of the original log file will bw stored into the backup folder