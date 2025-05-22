
# gfreplace — query-string replacement driven by gf-patterns

# DESCRIPTION
Tool based on [tomnomnom/qsreplace](https://github.com/tomnomnom/qsreplace) , [gf](https://github.com/tomnomnom/gf), and [gf-patterns](https://github.com/1ndianl33t/Gf-Patterns) combining value replacement with parameter filtering using JSON-defined patterns (gf-patterns).

It reads a list of URLs and replaces the values of query string parameters whose names match patterns defined in a JSON file. The replacement value can be specified by the user.

Unlike qsreplace, which replaces all parameter values, this tool only modifies the parameters explicitly listed in the pattern file. This gives the user more control over which variables are affected.

URLs that do not contain any parameters matching the provided patterns are automatically discarded from the output, making the tool work as a filter too.

# Install
1 - Download the project 
```git clone https://github.com/kadhajy/gfreplace.git```
2 - Download gf-patterns [gf-patterns](https://github.com/1ndianl33t/Gf-Patterns) or write you own json with patterns.
```git clone  https://github.com/1ndianl33t/Gf-Patterns.git```

# JSON
[gf-patterns](https://github.com/1ndianl33t/Gf-Patterns) already has files prepared to use, but if you want make your own, the json should look like this:
```
{
  "patterns": [
    "q=",
    "s=",
    "search=",
    "lang="
  ]
}

```

# Usage

```python3 gfreplace.py -u urls_list -j ./Gf-Patterns/xss.json -v '"><script>alert(1)</script>' -o output.txt```

### Usage Options
- `-h , --help`:       show help message and exit
- `-u [URLS]`:         file with urls, or - to stdin (default: '-')
- `-j JSON, --json JSON`:  path to json pattern file
- `-v VALUE, --value VALUE`: value to inject (default: 'REPLACED')
- `-o, --output`: File to save modified urls
- `--case-sesitive`: use case sentivie in patterns

# Tips
## Open Redirect
gau > gfreplace > httpx or openredirex
```
echo domain | gau | python3 gfreplace -j ./Gf-Patterns/redirect.json -v 'https://evil.com' | httpx -fr -sc -location -nc | grep -E "\[https://evil\.com\]
```
Or you can pipe the output directly to openredireX by using -v "FUZZ" with gfreplace, and -k "FUZZ" with openredireX.
## XSS
gau > gfreplace > httpx or grep
```
echo domain | gau | python3 gfreplace.py -j ~/.gf/xss.json -v '"><img src=x onerror=alert(1);>' | httpx -fr -ms '<img src=x onerror=alert(1);>'
```
