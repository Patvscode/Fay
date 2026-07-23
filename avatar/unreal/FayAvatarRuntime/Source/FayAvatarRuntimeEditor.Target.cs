using UnrealBuildTool;
using System.Collections.Generic;

// Experimental record only: Epic does not list LinuxArm64 in the default
// Editor platform class. This project-local opt-in was used to probe a native
// commandlet cooker, but the build is currently blocked by editor-only ARM64
// dependencies, including the FBX SDK. It is not a working or recommended cook
// path and does not change the platform support advertised by the engine.
[SupportedPlatforms("LinuxArm64")]
public class FayAvatarRuntimeEditorTarget : TargetRules
{
    public FayAvatarRuntimeEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        BuildEnvironment = TargetBuildEnvironment.Unique;
        bBuildAllModules = false;
        ExtraModuleNames.Add("FayAvatarRuntime");

        // Keep the native ARM64 cooker focused on project content and avoid
        // optional host integrations that are unnecessary for commandlets.
        bCompileCEF3 = false;
        bCompilePython = false;
        bCompileISPC = false;
        bCompileICU = false;
    }
}
