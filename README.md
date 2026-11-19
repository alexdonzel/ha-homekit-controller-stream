# HomeKit Controller with live streaming (test build)

Home Assistant's HomeKit Controller integration with live video for HomeKit cameras and video doorbells, instead of only snapshots.

## Status

A **test build**, not part of Home Assistant and not supported by the Home
Assistant project. It exists so the proposed changes can be used and tested on
real devices before they are released. Once they are in a Home Assistant
release, uninstall this and use the built-in integration again.

## What it changes

- Cameras paired over IP get a `homekit://` stream source, so Home Assistant streams their live video (and audio) through its built-in go2rtc over WebRTC. Cameras behind a HomeKit bridge keep snapshots only.

Proposed upstream in Home Assistant core; it follows [home-assistant/core#193419](https://github.com/home-assistant/core/pull/193419) and will be opened once that is merged.

Everything else is the built-in integration from the Home Assistant release
named in the version (`<release>.<build>`), unchanged.

## Install

It replaces the built-in `homekit_controller` integration, so install it only if you
want the change above.

1. Settings > Marketplace > ⋮ > Custom repositories, add
   `https://github.com/alexdonzel/ha-homekit-controller-stream` as an integration.
2. Install it, then restart Home Assistant.

Home Assistant logs a warning at startup that a custom `homekit_controller` integration
is in use; that is expected.

**Install [ha-go2rtc-homekit](https://github.com/alexdonzel/ha-go2rtc-homekit) too**: Home Assistant's built-in go2rtc does not accept `homekit://` sources yet. Without it cameras show a live view that never starts.

## Updates

A GitHub Action rebuilds this integration from each new Home Assistant release
within six hours of it, and publishes it as a new version. **After updating
Home Assistant, install the matching update here too**, or this copy keeps
running the previous release's integration code. If the build fails, the
changes no longer apply to the new release: uninstall this until it is fixed.

## Remove

Uninstall it in the Marketplace (or delete `custom_components/homekit_controller`) and
restart Home Assistant. Nothing else is changed.

## How it is built

`tools/build.py` takes `homeassistant/components/homekit_controller` from the release,
applies `patches/*.patch`, generates its translations and sets the
manifest's version, documentation and issue tracker. `custom_components/` is
generated: change the patches, not the output.

## Licence

Apache License 2.0, as Home Assistant. This repository contains Home Assistant
code, modified as described above.

## Security

A `homekit://` stream source contains Home Assistant's HomeKit pairing key for
the accessory, which lets whoever holds it control the accessory from your
network. It is only passed to Home Assistant's local go2rtc and is redacted from
go2rtc's log output, but treat Home Assistant logs as sensitive if you share
them. Re-pairing an accessory replaces its key.
