{
  description = "Evaluating lottery tickets";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, pyproject-nix, uv2nix, pyproject-build-systems }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        inherit (nixpkgs) lib;

        src = ./.;
        pyproject = pyproject-nix.lib.project.loadUVPyproject { projectRoot = src; };
        projectName = pyproject.pyproject.project.name;
        projectScripts = builtins.attrNames (pyproject.pyproject.project.scripts or { });

        pkgs = nixpkgs.legacyPackages.${system};
        defaultPythonPackage = pkgs.python314;
        pythonPackages = {
          default = defaultPythonPackage;
          "${projectName}" = defaultPythonPackage;
          "${projectName}-py314" = pkgs.python314;
        };

        workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = src; };
        overlay = workspace.mkPyprojectOverlay { sourcePreference = "wheel"; };

        mkPythonSet = pythonPackage:
          let
            baseSet = pkgs.callPackage pyproject-nix.build.packages { python = pythonPackage; };
          in
          baseSet.overrideScope (lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            overlay
          ]);

        mkPythonPackage = pythonPackageName: pythonPackage:
          let
            inherit (pkgs.callPackages pyproject-nix.build.util { }) mkApplication;
            pythonSet = mkPythonSet pythonPackage;
          in
          mkApplication {
            venv = pythonSet.mkVirtualEnv projectName workspace.deps.default;
            package = pythonSet."${projectName}";
          };

        mkApp = packageName: package: scriptName:
          lib.nameValuePair
            (if packageName == "default" then packageName else scriptName)
            { type = "app"; program = "${package}/bin/${scriptName}"; };

        mkAppsForAllScripts = packageName: package:
          builtins.listToAttrs (
            builtins.map (scriptName: mkApp packageName package scriptName) projectScripts
          );

        mkPythonShell = devShellName: pythonPackage:
          let
            pyprojectToml = "./pyproject.toml";
            venvDirectory = "./venv";
          in
          pkgs.mkShell {
            name = "${projectName}-development-environment";

            nativeBuildInputs = [
              pythonPackage
              pkgs.uv
              pkgs.basedpyright
              pkgs.ruff
            ];

            env = {
              UV_PROJECT_ENVIRONMENT = venvDirectory;
              UV_PYTHON = pythonPackage.interpreter;
              UV_PYTHON_DOWNLOADS = "never";
            };

            shellHook = /*sh*/ ''
              unset PYTHONPATH
              [ -f "${pyprojectToml}" ] && uv sync
              [ -d "${venvDirectory}" ] && source "${venvDirectory}/bin/activate"
            '';
          };
      in
      rec {
        packages = lib.mapAttrs mkPythonPackage pythonPackages;
        apps = lib.concatMapAttrs mkAppsForAllScripts packages;
        devShells = lib.mapAttrs mkPythonShell pythonPackages;
      }
    );
}
