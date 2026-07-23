using UnrealBuildTool;

public class FayAvatarRuntime : ModuleRules
{
    public FayAvatarRuntime(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PrivateDependencyModuleNames.AddRange(
            new string[]
            {
                "Core",
                "CoreUObject",
                "Engine",
                "FayAvatarBridge"
            });

        if (!Target.bBuildRequiresCookedData)
        {
            // The Spark development target compiles Vulkan shaders on demand.
            // UEBuildLinux narrows this TargetPlatform graph to LinuxArm64 and
            // Vulkan only, avoiding the x86-only OpenGL/VectorVM host tools.
            PrivateDependencyModuleNames.Add("TargetPlatform");
            DynamicallyLoadedModuleNames.Add("VulkanShaderFormat");
        }
    }
}
