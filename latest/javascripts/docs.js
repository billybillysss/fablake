(function () {
  function splitPath(pathname) {
    return pathname.split("/").filter(Boolean);
  }

  function withTrailingSlash(path) {
    if (!path.endsWith("/")) return path + "/";
    return path;
  }

  function scriptPrefix() {
    var script = document.querySelector('script[src$="javascripts/docs.js"]');
    if (!script) return "";
    var src = script.getAttribute("src") || "";
    return src.replace(/javascripts\/docs\.js$/, "");
  }

  function rewriteNavLinks(prefix) {
    var links = document.querySelectorAll("#sidebar-left a[href]");
    links.forEach(function (link) {
      var href = link.getAttribute("href") || "";
      if (!href || href.startsWith("http") || href.startsWith("#")) return;
      if (!href.endsWith(".md")) return;

      var rewritten = href.replace(/index\.md$/, "").replace(/\.md$/, "/");
      link.setAttribute("href", prefix + rewritten);
    });
  }

  function setupMobileNav() {
    var toggle = document.getElementById("menu-toggle");
    var sidebar = document.getElementById("sidebar-left");
    if (!toggle || !sidebar) return;
    toggle.addEventListener("click", function () {
      sidebar.classList.toggle("open");
    });
  }

  async function setupVersionPicker(prefix) {
    var select = document.getElementById("version-select");
    if (!select) return;
    var picker = select.closest(".version-picker");

    var response;
    try {
      response = await fetch(prefix + "versions.json", { cache: "no-store" });
      if (!response.ok) return;
    } catch (error) {
      return;
    }

    var manifest = await response.json();
    var versions = manifest.versions || [];
    if (!versions.length) {
      if (picker) picker.hidden = true;
      return;
    }

    if (versions.length < 2 && picker) {
      picker.hidden = true;
    }

    versions.forEach(function (entry) {
      var opt = document.createElement("option");
      opt.value = entry.key;
      opt.textContent = entry.label || entry.key;
      select.appendChild(opt);
    });

    var known = new Set(versions.map(function (entry) { return entry.key; }));
    var defaultKey = manifest.default || "latest";
    var currentPath = splitPath(window.location.pathname);
    var currentKey = defaultKey;
    var basePath = [];
    var relativePath = currentPath.slice();

    var versionIndex = -1;
    for (var i = 0; i < currentPath.length; i += 1) {
      if (known.has(currentPath[i])) {
        versionIndex = i;
        break;
      }
    }

    if (versionIndex >= 0) {
      currentKey = currentPath[versionIndex];
      basePath = currentPath.slice(0, versionIndex);
      relativePath = currentPath.slice(versionIndex + 1);
    }

    select.value = currentKey;

    var warning = document.getElementById("version-warning");
    var warningLink = document.getElementById("version-warning-link");
    if (warning && currentKey !== defaultKey && known.has(defaultKey)) {
      warning.hidden = false;
      if (warningLink) {
        var latestPath = "/" + basePath.concat([defaultKey]).concat(relativePath).join("/");
        warningLink.href = withTrailingSlash(latestPath);
      }
    }

    select.addEventListener("change", function () {
      var target = "/" + basePath.concat([select.value]).concat(relativePath).join("/");
      window.location.href = withTrailingSlash(target);
    });
  }

  var prefix = scriptPrefix();
  rewriteNavLinks(prefix);
  setupMobileNav();
  setupVersionPicker(prefix);
})();
