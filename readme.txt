┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│   Basic Concept                                                                                                                  │
│                                                                                             ┌────►  Purple.html                  │
│                                                                                             │      ┌──────────────┐              │
│                                                                                             │      │              │              │
│                                                                                             │      │ Purple       │              │
│                                                                                             │      │              │              │
│                                                                                             │      │ Grape        │              │
│                                                                                             │      │              │              │
│                                                                                             │      │ Item_3       │              │
│                                                                                             │      │              │              │
│                                                                                             │      │ Item_n       │              │
│                                                                                             │      └──────────────┘              │
│                                                                                             │                                    │
│                                                                                             │  ┌──► Red.html                     │
│                                                                                             │  │   ┌──────────────┐              │
│                              workingdata.csv                                                │  │   │              │              │
│                             ┌──────────────────────────────────────────────────────────┐    │  │   │ Red          │              │
│                             │Color, Fruit, Placeholder_3, Placeholder_n, ...           │    │  │   │              │              │
│     template.html           │                                                          │    │  │   │ Apple        │              │
│    ┌──────────────┐         │Purple, Grape, Item_3, Item_n                             ├────┘  │   │              │              │
│    │              │         │                                                          │       │   │ Item_3       │              │
│    │~Color        │         │Red, Apple, Item_3, Item_n                                ├───────┘   │              │              │
│    │              │         │                                                          │           │ Item_n       │              │
│    │~Placeholder_2│ ────►   │Green, Pear, Item_3, Item_n                               ├────────┐  └──────────────┘              │
│    │              │         │                                                          │        │                                │
│    │~Placeholder_3│         │Yellow, Banana, Item_3, Item_n                            ├───────┐└─► Green.html                   │
│    │              │         │                               .                          │       │   ┌──────────────┐              │
│    │~Placeholder_n│         │ .                               .                        ├────┐  │   │              │              │
│    └──────────────┘         │ .                                 .                      │    │  │   │ Green        │              │
│                             │ .                                                        │    │  │   │              │              │
│                             │                                                          │    │  │   │ Pear         │              │
│                             └──────────────────────────────────────────────────────────┘    │  │   │              │              │
│                                                                                             │  │   │ Item_3       │              │
│                                                                                             │  │   │              │              │
│                                                                                             │  │   │ Item_n       │              │
│                                                                                             │  │   └──────────────┘              │
│                                                                                             │  │                                 │
│                                                                                             │  └──► Yellow.html                  │
│                                                                                             │      ┌──────────────┐              │
│                                                                                             │      │              │              │
│                                                                                             │      │ Yellow       │              │
│                                                                                             │      │              │              │
│                                                                                             ▼      │ Banana       │              │
│                                                                                             .      │              │              │
│                                                                                             .      │ Item_3       │              │
│                                                                                             .      │              │              │
│                                                                                                    │ Item_n       │              │
│                                                                                                    └──────────────┘              │
│                                                                                                                                  │
│                                                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

CSV Format
Any spreadsheet software worth its salt will export to .csv, Use whichever you prefer. The first row (called row "0" in Python) is your column headers. They
correspond to the placeholders on your template. The rest of the spreadsheet is for your data. Each populated row will trigger a new copy of the HTML template.
It matches the text in each column header to placeholders in the template, then it replaces the placeholder with whatever is in the column on the current row. Each
new HTML file is named after the first entry in that row (modified slightly to ensure it is safe to use as a file name).

Headers can have any name as long as it matches something in the template. Image URLs are automatically detected, images are downloaded, and encoded into the HTML
via data URI scheme. To include a QR code, add a column with header "QR_TARGET" and give each row a directory like "https://example.com/files/" (it can be the same
directory for all rows). The resulting QR code image will point to the HTML file in that directory. For example if the first entry on a row is "Foo", the resulting
HTML file will be "Foo.html", and the QR code will point to "http://example.com/files/foo.html" (or whichever directory you provide under the "QR_TARGET" column).

Note that the program only reads the CSV file. Data from the CSV is edited in the script but the file you provide is never modified.

Template Format
The template HTML can have any format. The program runs a simple find-and-replace function on the raw HTML text. To avoid unintended edits (such as the "id" or "alt"
fields) it only replaces items preceded by a tilde "~". For example, if your spreadsheet has a column header called "Color", for each row of the spreadhseet it will
copy the template, search the copy for the string "~Color", and replace it with whatever is on that row under the "Color" column.

Placeholders for text might look something like this:

  <p class="TextBox" id="Description">~Description</p>
                                      ^^^^^^^^^^^^
For images, the placeholder should be in the source ("src") argument:

  <img id="image_1" alt="a pretty picture" src="~image_1">
                                                ^^^^^^^^
Note that the program only reads and copies the template. It does not edit the template itself.

Program Flow
┌─────────────────────────┐┌───────────────────────────┐┌──────────────────────┐
│template_path            ││data_path                  ││output_path           │
│(default="template.html")││(default="workingdata.csv")││(default="___TEST___")│
└─┬───────────────────────┘└──┬────────────────────────┘└──┬───────────────────┘
  │                           │                            │
  │   ┌───────────────────────┘                            │
  │   │                                                    │
  │   │   ┌────────────────────────────────────────────────┘
  │   │   │
  ▼   ▼   ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ main                                                                                                   │
│                                                                                                        │
│ Open data_path and load to nested list called data[]                                                   │
│                                                                                                        │
│ For each row in data (starting from the second row, i.e. data[1], not data[0])                         │
│                                                                                                        │
│     Make a copy of template_path and name it after the first item  in the current row (i.e data[i][0]) │    ┌──────────────────────┐
│                                                                                                        │  ┌►│ url_to_data_uri      │
│     For each item in the current row                                                                   │  │ │                      │  ┌─────────────────────────┐
│                                                                                                        │  │ │ Check is_image_url◄──│──│─►  is_image_url         │
│         Fetch any linked images using url_to_data_uri ─────────────────────────────────────────────────│──┘ │                      │  │                         │
│                                                                                                        │    │ Fetch image          │  │    If item is a url AND │
│     Make an index between each item in the current row and its associated column header (the first row)│    │                      │  │                         │
│                                                                                                        │    │ replace url with     │  │    If MIMEtype is /image│
│     Give this index and the template copy to find_and_replace ─────────────────────────────────────────│─┐  │  data URI scheme     │  │                         │
│                                                                                                        │ │  │  (This encodes the   │  │    Return TRUE          │
│     Save the new html file and move on the next row │                                                  │ │  │  image directly in   │  │                         │
│                                                     │                                                  │ │  │  the html)           │  └─────────────────────────┘
└─────────────────────────────────────────────────────┼──────────────────────────────────────────────────┘ │  │                      │
                                                      │                                                    │  └──────────────────────┘
                                                      │                                                    │
                                                      │                                                    │
                                                      ▼                                                    │    ┌───────────────────────────────────────────┐
                                          ┌────────────────────────────────────────────┐                   └──► │find_and_replace                           │
                                          │Output: {{output_path}}/{{data[i][0]}}.html │                        │                                           │
                                          └────────────────────────────────────────────┘                        │Find placeholders (columns headers preceded│
                                                                                                                │ by "~") and replace with the values from  │
                                                                                                                │ the current row                           │
                                                                                                                │                                           │
                                                                                                                │                                           │
                                                                                                                └───────────────────────────────────────────┘
