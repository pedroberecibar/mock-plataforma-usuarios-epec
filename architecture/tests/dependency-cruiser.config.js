/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    // Domain must not depend on anything internal except itself
    {
      name: "no-domain-to-infrastructure",
      severity: "error",
      comment: "Domain layer must not import from infrastructure",
      from: { path: "^src/domain" },
      to: { path: "^src/infrastructure" },
    },
    {
      name: "no-domain-to-interface",
      severity: "error",
      comment: "Domain layer must not import from interface/UI",
      from: { path: "^src/domain" },
      to: { path: "^src/(interface|ui|frontend)" },
    },

    // Application must not depend on infrastructure or interface
    {
      name: "no-application-to-infrastructure",
      severity: "error",
      comment: "Application layer must not import from infrastructure",
      from: { path: "^src/application" },
      to: { path: "^src/infrastructure" },
    },

    // No circular dependencies anywhere
    {
      name: "no-circular",
      severity: "error",
      comment: "Circular dependencies are forbidden",
      from: {},
      to: { circular: true },
    },

    // No orphan modules (unreachable code)
    {
      name: "no-orphans",
      severity: "warn",
      comment: "Orphan modules (not imported by anyone) should be reviewed",
      from: { orphan: true, pathNot: ["\\.(test|spec)\\.(js|ts)$", "index\\.(js|ts)$"] },
      to: {},
    },
  ],

  options: {
    doNotFollow: {
      path: "node_modules",
    },
    tsPreCompilationDeps: true,
    reporterOptions: {
      dot: {
        collapsePattern: "node_modules/[^/]+",
      },
      archi: {
        collapsePattern: "^(src/[^/]+)",
      },
    },
  },
};
