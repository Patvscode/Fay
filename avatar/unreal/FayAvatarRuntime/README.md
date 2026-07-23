# Fay Avatar Runtime

This is the minimal Unreal project used to compile and eventually package the
`FayAvatarBridge` plugin for Linux ARM64. It intentionally contains no
project-owned map or character assets yet. That keeps compiler and linker tests
independent of MetaHuman content.

The bridge uses Unreal's standard project-plugin layout so discovery, cooking,
and staging do not require an additional search path:

```text
avatar/unreal/
  FayAvatarRuntime/
    Plugins/
      FayAvatarBridge/
```

## Targets

- `FayAvatarRuntime` is the normal packaged Game target. It compiles for
  Linux ARM64, but it expects cooked content.
- `FayAvatarUncooked` is an experimental native-Spark diagnostic target. It
  builds shader and target-platform code into a Game executable to test ARM64
  startup. It is not a content cooker.
- `FayAvatarRuntimeEditor` is a retained editor-port experiment. It is not a
  working or supported Linux ARM64 editor target.

## Verified boundary

The normal runtime and bridge have compiled and linked as native ARM64 code.
The uncooked target has also launched through shader, plugin, and object-system
initialization.

It does not reach world creation or `BeginPlay`. Unreal stops while loading its
default material and texture objects because their source packages do not
contain the cooked Linux ARM64 platform data needed by a non-editor Game. The
files themselves are present. Consequently, the source-only bootstrap scene
has not run and should not be treated as a visual demo.

This limitation also applies to real character assets. A MetaHuman cannot be
made runtime-ready by the uncooked target; its meshes, materials, textures,
grooms, rigs, and map must be cooked first.

## Next build milestone

Use an editor-capable x86-64 Unreal 5.8 host to:

1. Add a small project-owned map.
2. Cook and package the project for `LinuxArm64` with Vulkan SM6.
3. Copy the package to the Spark and verify rendering, audio, and the local Fay
   connection before adding character content.

After the blank cooked package runs, add a lightweight skeletal character and
then an optimized free female MetaHuman assembly. Bind bridge mouth amplitude,
sentiment, and action events only after the basic packaged runtime is stable.

The project disables CEF and Python because neither is needed by the packaged
avatar runtime and their bundled Linux host dependencies are x86-64 oriented.

See the parent [Unreal status and architecture](../README.md) for the verified
results and the complete path to a working Spark renderer.
