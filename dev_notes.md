# Development Notes for human browser

### Introduction

This project is largely inspired by wmb-browser, and inherited a lot of code pieces from there.
Appreciation for that!

This browser is based on Dash Plotly, which is a powerful framework for building a data
visualization web-based application. Dash Plotly used a 'Reaction'-ish paradigm, which means
all the user actions or web page update is done through **callback** function. The `@callback`
decorator marks the callback function, which indicates the input, output, state, function logic, etc.
of a reaction to some user action or external change.
Please check [this link](https://dash.plotly.com/basic-callbacks) for more information.

Notice that any of the callback function has a global scope, which means no matter where
the callback function is, all the elements that matches its rule will be listened and
updated no matter where it is claimed. For example, for a callback function that is a
member function of a random class, it can still act on some HTML element that generated
in another class. True, this makes development relatively easy, but makes maintaining and debugging much harder. The function name of the callback function is not relevant to its
function, but typically follows an imperitive tone.1

This, in this project I just put different callback function into different files, depending on
the actual 'scope' of the callback function. I will go to detail in the next session.

### Architecture of human_browser

Similar to other front-end framework, each Dash Plotly has an entry point, which indicates
the manifest infomation of the application.
In this project, it is `human-browser/index.py`. It has a simple URL routing module, and some
html elements to be shown on the main page. The main human-browser is in the `/human_browser` page,
corresponding to the file `/apps/human_browser.py`

All other I layered the browser architecture into the following levels (from high to low):

- Web page elements and global call-back function.
  - `apps/human_browser.py` is the web page. It creates html elements and the layout, and implements the `add_panel` callback, which is used to create a panel of visualzation into the page.
- Figure/Panel level control:
  - This is implemented in the `viewmodel` folder. `FigureDiv.py` is the base class which defines a base input. ScatterPlotDiv creates a scatterplot for low-dim representation. HiGlassDiv creates a div for demonstrating snm3C data.
- Backend dataset. Here I reused the low-level data structure `Dataset` class developed by Hanqing as a base class. It is in `backend/dataset.py`. Then for human datset, I implemented an inherited class, `HumanDataset` (in `backend/human_dataset.py`), which loads the pre-compute human data and did everything needed to initizlie the human data.
