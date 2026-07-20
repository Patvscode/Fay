# Fay Unreal avatar work

This directory contains the source-only Fay bridge, a minimal Unreal project,
and the verified DGX Spark ARM64 findings. The intended final layout is:

```text
DGX Spark
  Fay HTTP and audio       http://127.0.0.1:5000
  Fay avatar WebSocket     ws://127.0.0.1:10002
  Packaged Unreal runtime  Linux ARM64, Vulkan
```

Fay owns conversation, speech, sentiment, and action data. Unreal owns the
character, rendering, audio playback, facial animation, and body animation.
The `FayAvatarBridge` plugin connects those two sides without a paid Unreal
plugin.

## Current status

The following has been verified on the DGX Spark in an isolated workspace:

- Unreal Engine 5.8.0 source at commit
  `7deeb413d3dc1fc034f48d1aacc0861301829d32` can run a native ARM64
  UnrealBuildTool bootstrap.
- The normal `FayAvatarRuntime` game target and the source-only
  `FayAvatarBridge` plugin compile and link as Linux ARM64 code.
- Native ARM64 ShaderConductor and DXC shared libraries build and load without
  missing dependencies, and the SPIR-V Reflect static library builds.
- Unreal has initialized the Spark's NVIDIA Vulkan device. This proves the GPU
  and Vulkan runtime path independently of avatar content.
- The experimental `FayAvatarUncooked` target compiles, launches, mounts the
  bridge plugin, initializes target-platform and shader systems, and reaches
  Unreal's object-system startup.

The following has **not** been completed or verified:

- The uncooked target does not reach world creation or `BeginPlay`. It stops
  while Unreal loads its default materials and textures, before the bootstrap
  scene can run.
- The source-only wireframe bootstrap has therefore not been displayed, and an
  end-to-end Fay message has not yet been exercised inside the Unreal runtime.
- No MetaHuman or other character has been imported, cooked, packaged, or
  rendered on the Spark.
- There is not yet a runnable cooked Linux ARM64 avatar package.

The default engine asset files are present. The failure is not a missing-file
problem: an uncooked non-editor Game process cannot construct the cooked
platform data required by Unreal materials, textures, meshes, and MetaHuman
content. Extending that process further would amount to porting a substantial
part of the editor asset pipeline, not writing a small Fay adapter.

## Supported route to a working character

Use an editor-capable x86-64 Unreal host to cook and package this project for
`LinuxArm64`, then copy the resulting package to the Spark. A temporary x86-64
Linux build machine is sufficient; the final renderer does not need that
machine after packaging.

The remaining sequence is:

1. Open the project with the matching Unreal 5.8 source branch on an
   editor-capable host.
2. Create a small project-owned map and package a blank `LinuxArm64` Vulkan
   application.
3. Run that cooked package on the Spark and verify display, audio, and the Fay
   WebSocket connection.
4. Add a lightweight skeletal character and verify jaw amplitude, idle motion,
   and one semantic gesture.
5. Add an optimized female MetaHuman assembly, then tune facial curves, LODs,
   hair cards, materials, and performance.

The Spark remains the final runtime host for Fay, speech services, AI models,
and the packaged Unreal application.

## Relationship to the published Fay UE5 demo

The `tianBosh/fay_agent` repository contains a README that points to
`xszyou/fay-ue5`; it does not contain an Unreal project or character assets.
The public `xszyou/fay-ue5` Git repository contains course material and images,
while its UE 5.6 Windows project is distributed separately through a Baidu
Drive archive. The course screenshots show four project dependencies:
BlueprintWebSocket, JSON Pro, Runtime Audio Importer, and Runtime MetaHuman Lip
Sync.

`FayAvatarBridge` replaces the first three transport/audio responsibilities
with Unreal source code that compiles for Linux ARM64. It deliberately does not
copy or require the paid Runtime MetaHuman Lip Sync plugin. The portable first
test uses PCM amplitude for jaw motion; higher-quality facial curves remain a
separate layer after a cooked MetaHuman package is running.

## Why the native editor experiment is not the main path

Epic's standard Unreal Editor target does not advertise Linux ARM64 support.
The project-local editor target was retained only as an engineering probe. It
passes the initial platform opt-in but is currently blocked by editor-only
native dependencies, including the absence of an ARM64 Linux FBX SDK. It is not
a working cooker and is not required by the final packaged application.

Similarly, `FayAvatarUncooked` is a diagnostic target for ARM64 compiler,
shader, and startup work. It is not a substitute for cooking content.

## Directory map

- `FayAvatarRuntime/Plugins/FayAvatarBridge/` — reusable source-only WebSocket,
  bounded HTTP audio, WAV, and avatar-event plugin.
- `FayAvatarRuntime/` — minimal game project and target definitions.
- `cook-linux-arm64.sh` — guarded BuildCookRun wrapper for an editor-capable
  x86-64 Linux UE 5.8 host.
- `verify-cooked-package.sh` — confirms the archive contains an AArch64 ELF
  executable and cooked content containers before deployment.

The local investigation also produced ordered patches against Epic's licensed
Unreal Engine source. Those records are intentionally ignored here: engine
source and derived patch material should be stored in a licensed/private
Unreal workspace or an authorized fork in Epic's UnrealEngine GitHub network,
not in this public Fay repository.

Do not place engine source, downloaded dependencies, cooked output, or build
artifacts in this repository. Keep them in a separate workspace and preserve
the source files here as the reproducible project input.
