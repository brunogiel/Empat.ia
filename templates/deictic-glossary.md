# Components of the product

Owns: the list of component names the reading step may use when it says what a participant was pointing at. Does not own: what each component does or how it performed → the session notes and `findings.md`.

One line per component, in this shape: `- CODE [tag]: what it is, in a few words`.
Use short codes in capitals, grouped by page or screen. Name what a person on the call would point at
(a card, a banner, the form, the menu), not the page as a whole.

Tags (optional, in square brackets after the code):

- `[sensitive]`: the component shows personal data (a form with a name, a mail or a phone, a
  confirmation page). Its rows get no capture in the sheet.
- `[outside]`: the component is not the product under test (the browser, the call window, a modal from
  another site). Its rows get no capture in the sheet.

Two answers are always valid and need no line here: `UNKNOWN` (the text and the frames are not enough)
and `NOT-APPLICABLE` (the phrase does not point at the screen).

## Page or screen 1

- PAGE1-header: title and the data under it
- PAGE1-body: main text of the page
- PAGE1-action: the main button or panel to act
- PAGE1-form [sensitive]: the form that asks for personal data

## Page or screen 2

- PAGE2-hero: the headline at the top
- PAGE2-menu: the navigation menu
- PAGE2-list: the list of items with its filters

## Outside the product

- SITE-navigation: logo, header or footer links, back and forward, scroll
- SITE-modal: a window over the site (a video, a notice on exit)
- BROWSER [outside]: address bar, tabs, system dialogs, other tabs
- CALL [outside]: the call window, the camera, the screen-share notice
- OTHER: something not in the list (describe it in `element`)
