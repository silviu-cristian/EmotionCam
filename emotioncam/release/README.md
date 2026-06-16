# EmotionCam Release Artifacts

Generated installer files are intentionally not committed to the source
repository because they are large binary release artifacts.

For public distribution, attach the installer generated from
`installer/emotioncam.iss` to a GitHub Release:

```text
EmotionCam_Setup.exe
```

The current build script and Inno Setup script produce the installer locally.
See the main README for release build steps.
