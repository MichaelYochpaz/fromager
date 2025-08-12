# Fromager User Guide

Welcome to the `fromager` user guide! This guide provides a comprehensive overview of how to use `fromager` for building Python wheel collections from source. Whether you're a new user getting started or an experienced developer looking to optimize your build process, this guide has something for you.

## Table of Contents

- [Concepts](#concepts)
- [Bootstrapping a Project](#bootstrapping-a-project)
- [Development vs. Production Workflows](#development-vs-production-workflows)
- [Building in Containers](#building-in-containers)
- [Scripting with Step Commands](#scripting-with-step-commands)
- [Uploading Builds](#uploading-builds)
- [Testing Plugins](#testing-plugins)
- [Example Production Pipeline](#example-production-pipeline)

## Concepts

`fromager` is a powerful tool for rebuilding a complete dependency tree of Python wheels from source. At its core, `fromager` is designed to give you full control over your build process, ensuring that every component of your Python environment—from the final application to its deepest dependencies and the build tools themselves—is built from source in a known, controlled environment.

This provides several guarantees:

1.  **Verifiable Origin**: The binary packages you install are built from a known source in a compatible environment.
2.  **Complete Source History**: All dependencies are also built from source, ensuring a full chain of custody.
3.  **Secure Build Tools**: The tools used for building are also built from source.
4.  **Customization**: The build process can be customized to patch bugs, apply different compiler options, or create build "variants" for different hardware or environments (e.g., `cpu` vs. `gpu`).

To achieve this, `fromager` is built around a few key concepts:

### Bootstrapping

Bootstrapping is the initial process of discovering and building the entire dependency tree for a set of top-level requirements. The `fromager bootstrap` command is the entry point for this workflow. It recursively:

1.  Resolves the versions of your top-level packages.
2.  Downloads their source code.
3.  Identifies and resolves their build-time and install-time dependencies.
4.  Builds each dependency in the correct order.
5.  Produces a `build-order.json` file, which is a flat list of packages in the order they need to be built.
6.  Produces a `graph.json` file, which represents the complete dependency graph.

This process creates a self-contained set of wheels and the instructions needed to replicate the build.

### Build Sequence

While bootstrapping is for discovery, the `build-sequence` command is designed for production builds. It takes a `build-order.json` file generated during bootstrapping and builds the packages in the specified order. This process is not recursive; it assumes the build order is complete and correct. This separation allows for more predictable and controlled production builds.

### Step Commands

For even more granular control, `fromager` provides a series of `step` commands. These commands break down the build process into individual actions, such as:

-   `step download-source-archive`: Downloads the source code for a package.
-   `step prepare-source`: Unpacks the source and applies any patches.
-   `step prepare-build`: Sets up the build environment.
-   `step build-sdist`: Creates a source distribution.
-   `step build-wheel`: Builds the final wheel.

These commands allow you to script complex workflows, such as performing certain steps in different environments or with different configurations.

### Key Files

The `fromager` workflow revolves around a few key files:

-   **`requirements.txt`**: Your initial list of top-level packages.
-   **`constraints.txt`**: An optional file to constrain the versions of dependencies.
-   **`build-order.json`**: The output of the bootstrap process, defining the build order for production.
-   **`graph.json`**: A detailed dependency graph, useful for understanding the relationships between packages and for enabling repeatable builds.

## Bootstrapping a Project

Bootstrapping is the first step in using `fromager` to build a collection of wheels. This process discovers all the necessary dependencies for your project and creates a plan to build them.

### The Bootstrap Process

The `fromager bootstrap` command automates the following steps:

1.  **Create Input Files**:
    *   **`requirements.txt`**: A list of your project's top-level dependencies.
    *   **`constraints.txt`**: An optional file to specify version constraints for any dependency in the tree.

2.  **Run the `bootstrap` Command**:
    ```bash
    fromager bootstrap --requirements-file requirements.txt --constraints-file constraints.txt
    ```

3.  **Dependency Resolution**: `fromager` will:
    *   Recursively resolve all dependencies, starting with your top-level requirements.
    *   Download the source code for each package.
    *   Build each package in the correct order, ensuring that dependencies are built before the packages that need them.

4.  **Handle Build Failures**: If a package fails to build, you can:
    *   **Mark as Pre-built**: Create a settings file for the package and mark it as `pre_built`. This allows you to continue the bootstrap process and identify other potential issues.
    *   **Debug and Patch**: Once you have a complete list of problematic packages, you can work on fixing them by applying patches or making other customizations.

5.  **Review the Output**: Once the bootstrap process completes successfully, you will have:
    *   A `wheels-repo` directory containing all the built wheels.
    *   A `sdists-repo` directory containing the source distributions.
    *   A `work-dir` directory with logs and other build artifacts.
    *   A `build-order.json` file, which is the input for your production builds.
    *   A `graph.json` file, which shows the complete dependency graph.

### Example Bootstrap Session

Here is a simplified example of a bootstrap session for the `pydantic-core` package.

1.  **Start with a `requirements.txt` file**:
    ```
    pydantic-core==2.18.4
    ```

2.  **Run the `bootstrap` command**:
    ```bash
    fromager bootstrap --requirements-file requirements.txt
    ```

3.  **Monitor the Output**: `fromager` will log its progress as it resolves dependencies and builds each package.

4.  **Address Failures**: If a build fails (for example, due to a missing compiler or an incorrect dependency), you can create a patch or a settings file to address the issue and then re-run the bootstrap command.

By the end of the bootstrap process, you will have a complete, self-contained set of wheels and the necessary files to create repeatable production builds.

## Development vs. Production Workflows

`fromager` is designed to support two distinct workflows: one for development and discovery, and another for robust, repeatable production builds. Understanding the differences between these workflows is key to using the tool effectively.

### Development Workflow: Bootstrapping and Discovery

The development workflow is centered around the `fromager bootstrap` command. This mode is designed for exploration and for creating the initial build configuration.

**Key Characteristics:**

-   **Recursive Dependency Resolution**: `bootstrap` starts with a small set of top-level requirements and recursively discovers the entire dependency tree.
-   **Focus on Discovery**: The primary goal is to identify all the packages that need to be built and the order in which to build them.
-   **Iterative Debugging**: This workflow is ideal for identifying and fixing build issues. You can use techniques like the `pre_built` flag and patching to work through problematic packages one by one.
-   **Output for Production**: The main outputs of the bootstrap process are the `build-order.json` and `graph.json` files, which are the inputs for the production workflow.

**When to Use It:**

-   When you are setting up a new project or a new set of requirements.
-   When you need to identify the full set of dependencies for a project.
-   When you are debugging build failures for specific packages.

### Production Workflow: Repeatable and Controlled Builds

The production workflow is designed for building packages in a controlled and repeatable manner. It relies on the outputs of the development workflow and uses the `build` and `build-sequence` commands.

**Key Characteristics:**

-   **Non-Recursive**: Production builds are not recursive. They follow the explicit instructions in the `build-order.json` file.
-   **Predictable and Repeatable**: Because the build order is predetermined, production builds are highly predictable and repeatable.
-   **Optimized for Automation**: The `build-sequence` command is designed to be used in automated CI/CD pipelines.
-   **Focused on Building**: This workflow is focused on executing the build, not discovering dependencies.

**When to Use It:**

-   In your CI/CD pipeline for automated builds.
-   When you need to build a set of packages in a known, controlled environment.
-   When you need to ensure that your builds are repeatable and consistent.

### Summary of Differences

| Feature                      | Development Workflow (`bootstrap`)                               | Production Workflow (`build-sequence`)                               |
| ---------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------- |
| **Primary Goal**             | Discover dependencies and create a build plan.                   | Execute a predetermined build plan.                                  |
| **Dependency Resolution**    | Recursive; discovers the full dependency tree.                   | Non-recursive; follows the `build-order.json` file.                  |
| **Input**                    | `requirements.txt`, `constraints.txt`                            | `build-order.json`                                                   |
| **Output**                   | `build-order.json`, `graph.json`, and a full set of built wheels. | A full set of built wheels.                                          |
| **Ideal Use Case**           | Initial project setup, debugging, and dependency exploration.    | Automated CI/CD pipelines and repeatable production builds.          |

## Building in Containers

Using containers is a recommended approach for building with `fromager`, as it provides a consistent and reproducible build environment, isolating your builds from the host system and ensuring that they are portable. This section provides a guide on how to set up and use a container-based workflow.

### Overview

The container-based workflow involves these key steps:

1.  **Define a `Containerfile`**: Create a `Containerfile` to define the build environment, including the base image, system dependencies, and `fromager` installation.
2.  **Create a Build Script**: Write a shell script (e.g., `bootstrap.sh`) to automate the process of building the container image and running `fromager` within it.
3.  **Run the Build**: Execute the build script, which will build the container, mount the necessary directories, and run the `fromager bootstrap` command.
4.  **Iterate and Debug**: If a build fails, use `fromager`'s features, such as the `pre_built` flag and patching, to debug and fix the issues iteratively.

### The `Containerfile`

The `Containerfile` is used to define the build environment. Here is an example that sets up a Red Hat Universal Base Image (UBI) with Python, Rust, and `fromager`:

```dockerfile
# Simple image definition demonstrating building with system dependencies in a
# repeatable way.

ARG RHEL_MINOR_VERSION=9.4
FROM registry.access.redhat.com/ubi9/ubi:${RHEL_MINOR_VERSION}

USER 0

# install patch for fromager
# install rust for building pydantic-core
RUN dnf install -y --nodocs \
    patch rust cargo \
    && dnf clean all

# /opt/app-root structure (same as s2i-core and ubi9/python-311)
ENV APP_ROOT=/opt/app-root \
    HOME=/opt/app-root/src \
    PATH=/opt/app-root/src/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Python, pip, and virtual env settings
ARG PYTHON_VERSION=3.11
ENV PYTHON_VERSION=${PYTHON_VERSION} \
    PYTHON=python${PYTHON_VERSION} \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONIOENCODING=utf-8 \
    PS1="(app-root) \w\$ "

RUN dnf install -y --nodocs \
    ${PYTHON} \
    ${PYTHON}-devel \
    && dnf clean all

# Set up a virtualenv to hold fromager
ENV VIRTUAL_ENV=${APP_ROOT}
RUN ${PYTHON} -m venv --upgrade-deps ${VIRTUAL_ENV} \
    && mkdir ${HOME}
ENV PATH=${VIRTUAL_ENV}/bin:$PATH

# Install the build tools
RUN ${PYTHON} -m pip install fromager

CMD /bin/bash

# Tell fromager what variant to build with this image
ENV FROMAGER_VARIANT=cpu-ubi9

WORKDIR /work

# Install the fromager settings to the work directory
COPY ./overrides /work/overrides
```

### The Build Script

The `bootstrap.sh` script automates the build process. It builds the container image and then runs `fromager` inside it, mounting the necessary input and output directories.

```bash
#!/bin/bash

# ... (script arguments parsing) ...

# Build the builder image
podman build \
       -f "$CONTAINERFILE" \
       -t "$IMAGE" \
       .

# Run fromager in the image to bootstrap the requirements file.
podman run \
       -it \
       --rm \
       --security-opt label=disable \
       --volume "./$OUTDIR:/work/bootstrap-output:rw,exec" \
       --volume "./$CCACHE_DIR:/var/cache/ccache:rw,exec" \
       --volume "${CONSTRAINTS_FILE}:/bootstrap-inputs/constraints.txt" \
       --volume "${REQUIREMENTS_FILE}:/bootstrap-inputs/requirements.txt" \
       --ulimit host \
       --pids-limit -1 \
       "$IMAGE" \
       sh -c "$COMMAND; sleep $KEEPALIVE"
```

### Debugging Workflow

When a package fails to build, you can use an iterative process to debug and fix the issue:

1.  **Identify the Error**: Examine the build logs to find the root cause of the failure.
2.  **Use the `pre_built` Flag**: To isolate the problematic package, you can mark it as `pre_built` in a package-specific settings file. This allows the rest of the dependencies to be processed.
3.  **Apply Patches**: Once the issue is identified, you can apply patches to the source code to fix the build.
4.  **Re-run the Build**: Remove the `pre_built` flag and re-run the build to verify that the patch resolves the issue.

## Scripting with Step Commands

For ultimate control over the build process, `fromager` provides a set of `step` commands. These commands allow you to break down the `build` and `build-sequence` operations into their constituent parts, which is useful for scripting complex workflows, debugging, or running different stages of the build in different environments.

### Available Step Commands

-   **`step download-source-archive`**: Finds and downloads the source distribution for a specific version of a package from a package index.

    ```bash
    fromager step download-source-archive --sdist-server-url https://pypi.org/simple/ mypackage==1.2.3
    ```

-   **`step prepare-source`**: Unpacks a downloaded source archive and applies any configured patches.

    ```bash
    fromager step prepare-source mypackage==1.2.3
    ```

-   **`step prepare-build`**: Creates an isolated virtual environment and installs the build dependencies for a package.

    ```bash
    fromager step prepare-build --wheel-server-url http://localhost:8080/simple mypackage==1.2.3
    ```

-   **`step build-sdist`**: Creates a new source distribution (`sdist`) from the prepared source tree, including any patches or other modifications.

    ```bash
    fromager step build-sdist mypackage==1.2.3
    ```

-   **`step build-wheel`**: Builds the final wheel from the prepared source and build environment.

    ```bash
    fromager step build-wheel mypackage==1.2.3
    ```

### Example Workflow

Here is an example of how you could use the `step` commands to build a single package:

```bash
# 1. Download the source
fromager step download-source-archive --sdist-server-url https://pypi.org/simple/ mypackage==1.2.3

# 2. Prepare the source (unpack and patch)
fromager step prepare-source mypackage==1.2.3

# 3. Prepare the build environment
fromager step prepare-build --wheel-server-url http://localhost:8080/simple mypackage==1.2.3

# 4. Build the sdist
fromager step build-sdist mypackage==1.2.3

# 5. Build the wheel
fromager step build-wheel mypackage==1.2.3
```

This level of control is particularly useful in scenarios where, for example, you need to download sources in a networked environment and then perform the builds in an isolated, offline environment.

## Uploading Builds

`fromager` provides a flexible mechanism for uploading your built wheels to a package index using the `post_build` hook. This allows you to integrate `fromager` with your existing artifact management and CI/CD workflows.

### Upload Strategies

You have two primary strategies for uploading builds, each with its own trade-offs:

1.  **Upload at the End of the Build Sequence**: This is the recommended approach for production builds. After the `build-sequence` command completes, you will have a `wheels-repo` directory containing all of your built wheels. You can then use a tool like `twine` to upload the entire contents of this directory to your package index. This approach is simple, robust, and ensures that you are only uploading a complete and consistent set of wheels.

2.  **Upload One by One Using the `post_build` Hook**: For more immediate feedback or for workflows where you need to upload wheels as soon as they are built, you can use the `post_build` hook. This hook is run after each wheel is successfully built and can be used to trigger an upload to your package index.

### Using the `post_build` Hook

To use the `post_build` hook, you need to:

1.  **Create a Hook Function**: Write a Python function that takes the build context and file paths as arguments and contains the logic for uploading the wheel.

    ```python
    # package_plugins/module.py
    import logging
    import pathlib
    from packaging.requirements import Requirement
    from fromager import context

    logger = logging.getLogger(__name__)

    def upload_wheel(
        ctx: context.WorkContext,
        req: Requirement,
        dist_name: str,
        dist_version: str,
        sdist_filename: pathlib.Path,
        wheel_filename: pathlib.Path,
    ):
        logger.info(f"Uploading {wheel_filename} to package index...")
        # Add your upload logic here, e.g., using twine or another tool
    ```

2.  **Register the Hook in `pyproject.toml`**: Register your hook function as an entry point in your `pyproject.toml` file.

    ```toml
    [project.entry-points."fromager.hooks"]
    post_build = "package_plugins.module:upload_wheel"
    ```

Now, every time `fromager` successfully builds a wheel, it will call your `upload_wheel` function, passing in the necessary information to upload the wheel.

**Note**: The `post_build` hook is not run for pre-built wheels. If you need to perform actions on pre-built wheels, use the `prebuilt_wheel` hook instead.

## Testing Plugins

`fromager`'s plugin architecture allows for extensive customization of the build process. While creating plugins is an advanced topic, testing them is a straightforward process. This section provides guidance on how to test both hook-based and override-based plugins, using a CI-like approach.

### Testing Strategy

The most effective way to test `fromager` plugins is to create end-to-end tests that simulate a real build process. This involves:

1.  **Creating a Test Package**: A simple Python package that contains your plugin logic.
2.  **Writing a Test Script**: A shell script that installs the test package, runs `fromager`, and verifies the results.
3.  **Running in a CI Environment**: Integrating these tests into your CI pipeline to ensure that your plugins are always tested against the latest version of your code.

### Testing Hook-Based Plugins

Hook-based plugins are registered using entry points in `pyproject.toml` and are triggered at specific points in the build process.

**1. Create the Plugin Package:**

-   **`pyproject.toml`**: Define the project and register the hook.

    ```toml
    [project.entry-points."fromager.hooks"]
    post_bootstrap = "package_plugins.hooks:after_bootstrap"
    ```

-   **`package_plugins/hooks.py`**: Implement the hook function.

    ```python
    def after_bootstrap(ctx, req, dist_name, dist_version, sdist_filename, wheel_filename):
        # Create a file to signal that the hook was called
        test_file = ctx.work_dir / "test-output-file.txt"
        test_file.write_text(f"{dist_name}=={dist_version}")
    ```

**2. Create the Test Script:**

-   **`test_post_bootstrap_hook.sh`**: A shell script to run the test.

    ```bash
    #!/bin/bash
    # Install the plugin package
    pip install ./e2e/fromager_hooks

    # Run fromager
    fromager bootstrap some_package

    # Verify the results
    if [ ! -f "work-dir/test-output-file.txt" ]; then
        echo "FAIL: Hook did not create output file."
        exit 1
    fi
    ```

### Testing Override-Based Plugins

Override-based plugins are used to customize the build process for a specific package.

**1. Create the Plugin Package:**

-   **`pyproject.toml`**: Define the project and register the override.

    ```toml
    [project.entry-points."fromager.project_overrides"]
    stevedore = "package_plugins.stevedore"
    ```

-   **`package_plugins/stevedore.py`**: Implement the override function.

    ```python
    def build_sdist(ctx, extra_environ, req, sdist_root_dir, version, build_env):
        # Add custom logic here, or call the default implementation
        return sources.pep517_build_sdist(...)
    ```

**2. Create the Test Script:**

-   The test script for an override plugin would be similar to the hook-based plugin test. It would install the plugin package, run `fromager` on the package that the override applies to, and then verify that the build was successful and that the override was applied correctly.

By following these patterns, you can create a robust set of tests for your `fromager` plugins, ensuring that they are reliable and work as expected in your build environment.

## Example Production Pipeline

This section outlines a conceptual production pipeline that leverages `fromager` to build, test, and deploy a Python application. This example assumes a CI/CD environment like Jenkins, GitLab CI, or GitHub Actions.

### Pipeline Stages

A typical production pipeline using `fromager` can be broken down into the following stages:

1.  **Bootstrap (Manual/Semi-Automated)**: This initial stage is for dependency discovery and is typically run when new dependencies are added or updated.
2.  **Build (Automated)**: This stage is triggered by changes to the source code and builds all the necessary wheels.
3.  **Test (Automated)**: This stage runs tests against the newly built wheels to ensure they are working correctly.
4.  **Publish (Automated)**: This stage publishes the built wheels to a private package index.
5.  **Deploy (Automated)**: This stage deploys the application using the wheels from the private package index.

### Pipeline Flow Diagram

```
+-------------------+      +------------------+      +----------------+      +-----------------+      +----------------+
|                   |      |                  |      |                |      |                 |      |                |
|  1. Bootstrap     +----->|  2. Build        +----->|  3. Test       +----->|  4. Publish      +----->|  5. Deploy     |
|  (Manual)         |      |  (CI/CD)         |      |  (CI/CD)       |      |  (CI/CD)        |      |  (CI/CD)       |
|                   |      |                  |      |                |      |                 |      |                |
+-------------------+      +------------------+      +----------------+      +-----------------+      +----------------+
        |                          |                       |                       |                        |
        |                          |                       |                       |                        |
+-------v----------+     +---------v--------+     +--------v-------+     +----------v------+     +----------v-----+
| fromager         |     | fromager         |     | pytest         |     | twine upload    |     | ansible-playbook |
| bootstrap        |     | build-sequence   |     | (or other      |     | (or other tool) |     | (or other tool)  |
|                  |     |                  |     | test runner)   |     |                 |     |                  |
+------------------+     +------------------+     +----------------+     +-----------------+     +------------------+
```

### Stage Details

**1. Bootstrap**

-   **Trigger**: Manual, or semi-automated when `requirements.txt` changes.
-   **Action**: Run the `fromager bootstrap` command to generate the `build-order.json` and `graph.json` files.
-   **Artifacts**: `build-order.json`, `graph.json`. These should be committed to your source control repository.

**2. Build**

-   **Trigger**: A push to the main branch or the creation of a pull request.
-   **Action**:
    -   Check out the source code, including the `build-order.json` file.
    -   Run the `fromager build-sequence` command within a containerized build environment.
-   **Artifacts**: The `wheels-repo` directory, containing all the built wheels.

**3. Test**

-   **Trigger**: Successful completion of the Build stage.
-   **Action**:
    -   Create a new virtual environment.
    -   Install the newly built wheels from the `wheels-repo` directory.
    -   Run your project's test suite (e.g., using `pytest`).
-   **Artifacts**: Test reports.

**4. Publish**

-   **Trigger**: Successful completion of the Test stage on the main branch.
-   **Action**:
    -   Use a tool like `twine` to upload the contents of the `wheels-repo` directory to your private package index.
-   **Artifacts**: The published wheels in your package index.

**5. Deploy**

-   **Trigger**: Successful completion of the Publish stage.
--   **Action**:
    -   Trigger your deployment process (e.g., using Ansible, Docker, or another deployment tool).
    -   The deployment process will install the application and its dependencies from your private package index.
-   **Artifacts**: A new version of your application running in production.

By structuring your pipeline in this way, you can leverage `fromager` to create a robust, secure, and repeatable build and deployment process for your Python applications, giving you full confidence in the integrity of your software supply chain.
