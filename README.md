# stisys-watcher
A script that detects changes in the graduation result system 
([stisys](https://stisys.haw-hamburg.de/)) of the [Hamburg University 
of Applied Sciences](https://www.haw-hamburg.de/).

## Usage
You can use this script in different ways though "Full-automated query" is advised.

### Interactive query
To interactively query the stisys simply run the script: `python3 stisys-watcher.py`

You will be asked to provide your username as well as your password. After the request 
completed the differences will be displayed in the console.

### Semi-automated query
Supplying all required information via cli arguments is also supported. Run the following 
to automatically use the given username/password and suppress any unnecessary output.
```
python3 stisys-watcher.py -u YOUR_USERNAME -p YOUR_PASSWORD -s
```

#### Read credentials from file
To prevent user credentials from being visible within the process call the script is 
able to read them from a JSON based credential file:
```
# Create the file once
cat >stisys.cred <<EOL
{
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD"
}
EOL
chmod 600 stisys.cred
```

After creation of the credential file run the script:
```
python3 stisys-watcher.py -c stisys.cred -s
```

### Full-automated query
To fully automate the script and get the results via mail you can automatically run it 
via `cron`. To do so add the following line to your crontab (e.g. via `crontab -e`) and 
adjust the file paths according to your setup:
```
MAILTO=your@email.com
@hourly python3 /your/path/stisys-watcher.py -c /your/path/stisys.cred -f /your/path/difffile -s
```

This will run the script once every hour. `cron` then sends you a mail, if not disabled 
in `cron`, as soon as new results have been detected.

## Options and arguments
```
usage: stisys-watcher.py [-h] [-u USERNAME] [-p PASSWORD] [-s]
                         [-f DIFFFILE_PATH] [-c CREDFILE]

Automatically pull new results from Stisys (HAW Hamburg).

optional arguments:
  -h, --help        show this help message and exit
  -u USERNAME       Your HAW username (a-idenfitier)
  -p PASSWORD       Your HAW password
  -s                Silent mode. Suppresses output apart from result.
  -f DIFFFILE_PATH  Use custom file to store last query state.
  -c CREDFILE       Load credentials from file.
```

## License
This project is licensed under the terms of the MIT license. See `LICENSE.txt`.
