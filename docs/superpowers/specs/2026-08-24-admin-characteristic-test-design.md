# Admin characteristic test design

## Problem

`test_admin_bird_characteristic_options_include_descriptions` creates a
`BirdCharacteristic` instance but never uses the resulting `characteristic`
variable. This triggers the unused-variable finding the test should avoid.

## Design

Add `self.assertContains(response, characteristic.name)` to the existing test.
This uses the created object directly and verifies that its characteristic name
(`Tail`) is rendered in the admin inline choice list, complementing the
existing description and JavaScript hook assertions.

No application code, fixtures, or test setup changes are required.

## Testing

Run the focused Django test for
`BirdAppAdminTest.test_admin_bird_characteristic_options_include_descriptions`.
