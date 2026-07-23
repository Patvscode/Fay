using UnrealBuildTool;
using System.Collections.Generic;

// Native DGX Spark Vulkan/global-shader smoke target. It deliberately avoids
// the FBX-dependent UnrealEditor stack; real avatar assets still need to be
// cooked by an editor-capable host before the normal runtime can load them.
[SupportedPlatforms("LinuxArm64")]
public class FayAvatarUncookedTarget : TargetRules
{
    public FayAvatarUncookedTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        BuildEnvironment = TargetBuildEnvironment.Unique;
        ExtraModuleNames.Add("FayAvatarRuntime");

        bBuildRequiresCookedData = false;
        bBuildWithEditorOnlyData = false;
        bBuildDeveloperTools = false;
        bForceBuildTargetPlatforms = true;
        bForceBuildShaderFormats = true;

        // TargetPlatform normally exists only in Editor/Program processes.
        // This unique smoke target loads it solely to compile Vulkan global
        // shaders in-process on LinuxArm64.
        GlobalDefinitions.Add("UE_WITH_UNCOOKED_TARGET_PLATFORM_DATA=1");

        bCompileCEF3 = false;
        bCompilePython = false;
        bCompileISPC = false;
        bCompileICU = false;
    }
}
