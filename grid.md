# ToDo

If we are going to use Gridstack, there are a few things we need to do

We still cannot use svgs. Our svgs are too complex and rendering takes a lot. So
we still need to render them to a canvas.

That means we need to hijack the resizing event or drawing event or whatever it
is that Gridstack emits to redraw/resize stuff on our display canvases

With that in mind I suggest that we set up configurations that we can pass stuff
in as. Those configurations also get written to local storage.

The page reads JSON every 15 minutes, sees what changes, and then if it needs to
reloads the image.

So...

Checklist of things to do:

- [x] Find out how to dynamically fit an svg to a canvas that sits in a Gridstack ele
- [x] Fit the image reloading function chatgpt made to the canvas process
- [x] Create a configuration and have that load and be referred to when having
  to resize
- [x] Allow the user to add or remove elements with the console and write that
  configuration to localstorage for exporting and persistence.
