using UnrealBuildTool;
using System.Collections.Generic;

public class FayAvatarRuntimeTarget : TargetRules
{
    public FayAvatarRuntimeTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("FayAvatarRuntime");

        // The packaged avatar does not need browser or Python editor support.
        bCompileCEF3 = false;
        bCompilePython = false;

        // Epic's bundled Linux ISPC host tool is x86-64-only. Runtime modules
        // use their scalar C++ fallbacks for this native ARM64 build.
        bCompileISPC = false;

        // The downloaded ARM64 ICU archive was built against libc++, while
        // this native system-toolchain bootstrap uses libstdc++. Keep the
        // first runtime ABI-consistent; MetaHuman/avatar rendering does not
        // require ICU's full localization and regex implementation.
        bCompileICU = false;
    }
}
