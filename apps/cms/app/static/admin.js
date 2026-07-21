(function () {
  "use strict";

  function parseJson(value, fallback) {
    try {
      return JSON.parse(value);
    } catch (_err) {
      return fallback;
    }
  }

  function mediaItemsFromPage() {
    var node = document.getElementById("media-data");
    if (!node) return [];
    return parseJson(node.textContent || "[]", []);
  }

  function addMediaItemToPageStore(item) {
    var store = document.getElementById("media-data");
    if (!store) return;
    var items = parseJson(store.textContent || "[]", []);
    items.unshift(item);
    store.textContent = JSON.stringify(items);
  }

  function openMediaPicker(onSelect) {
    var overlay = document.createElement("div");
    overlay.className = "media-picker";
    overlay.innerHTML =
      '<div class="media-picker__dialog">' +
      '<header><h3>Wybierz media</h3><button type="button" class="link-button" data-close>Zamknij</button></header>' +
      '<form class="media-picker__upload form-stack" data-picker-upload>' +
      '<label>Prześlij nowe zdjęcie<input type="file" name="file" accept="image/jpeg,image/png,image/webp,image/avif,image/svg+xml" required></label>' +
      '<label>Tekst alternatywny (alt)<input type="text" name="alt_text" maxlength="240" required placeholder="Opis zdjęcia"></label>' +
      '<button class="button button--small button--accent" type="submit">Prześlij i użyj</button>' +
      '<p class="media-picker__upload-status" data-upload-status></p>' +
      "</form>" +
      '<div class="media-picker__grid"></div>' +
      "</div>";

    var grid = overlay.querySelector(".media-picker__grid");
    var uploadForm = overlay.querySelector("[data-picker-upload]");
    var status = overlay.querySelector("[data-upload-status]");

    function renderGrid() {
      var items = mediaItemsFromPage();
      grid.innerHTML = "";
      if (!items.length) {
        grid.innerHTML = '<p class="empty">Brak plików. Prześlij zdjęcie powyżej.</p>';
        return;
      }
      items.forEach(function (item) {
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "media-picker__item";
        btn.innerHTML =
          '<img src="' +
          item.url +
          '" alt="">' +
          "<span>" +
          (item.file_name || item.alt_text || "plik") +
          "</span>";
        btn.addEventListener("click", function () {
          onSelect(item);
          overlay.remove();
        });
        grid.appendChild(btn);
      });
    }

    uploadForm.addEventListener("submit", function (event) {
      event.preventDefault();
      var data = new FormData(uploadForm);
      var submitBtn = uploadForm.querySelector("button[type=submit]");
      submitBtn.disabled = true;
      status.textContent = "Przesyłanie...";
      fetch("/api/admin/media", { method: "POST", body: data })
        .then(function (response) {
          if (!response.ok) throw new Error("Upload nieudany");
          return response.json();
        })
        .then(function (uploaded) {
          var item = {
            id: String(uploaded.id),
            url: uploaded.url,
            file_name: uploaded.alt_text || "plik",
            alt_text: uploaded.alt_text || "",
          };
          addMediaItemToPageStore(item);
          status.textContent = "";
          submitBtn.disabled = false;
          onSelect(item);
          overlay.remove();
        })
        .catch(function (err) {
          status.textContent = err.message || "Błąd uploadu";
          submitBtn.disabled = false;
        });
    });

    overlay.addEventListener("click", function (event) {
      if (event.target === overlay || event.target.matches("[data-close]")) {
        overlay.remove();
      }
    });
    document.body.appendChild(overlay);
    renderGrid();
  }

  function initBlockEditor(root) {
    var input = root.querySelector('input[type="hidden"][name="content_json"], textarea[name="content_json"]');
    var list = root.querySelector("[data-blocks]");
    if (!input || !list) return;

    var data = parseJson(input.value || '{"blocks":[]}', { blocks: [] });
    var blocks = Array.isArray(data.blocks) ? data.blocks : [];

    function sync() {
      input.value = JSON.stringify({ blocks: blocks }, null, 0);
    }

    function render() {
      list.innerHTML = "";
      blocks.forEach(function (block, index) {
        var card = document.createElement("article");
        card.className = "block-card";
        card.draggable = true;
        card.dataset.index = String(index);

        var head =
          '<div class="block-card__head">' +
          '<span class="block-card__type">' +
          block.type +
          "</span>" +
          '<div class="block-card__actions">' +
          '<button type="button" data-up title="Wyżej">↑</button>' +
          '<button type="button" data-down title="Niżej">↓</button>' +
          '<button type="button" data-remove title="Usuń">×</button>' +
          "</div></div>";

        var body = "";
        if (block.type === "heading") {
          body =
            '<label>Poziom<select data-field="level">' +
            '<option value="2"' +
            (block.level !== 3 ? " selected" : "") +
            ">H2</option>" +
            '<option value="3"' +
            (block.level === 3 ? " selected" : "") +
            ">H3</option>" +
            '</select></label><label>Tekst<textarea data-field="text" rows="2">' +
            (block.text || "") +
            "</textarea></label>";
        } else if (block.type === "list") {
          body =
            '<label>Elementy (jeden w linii)<textarea data-field="items" rows="4">' +
            (block.items || []).join("\n") +
            "</textarea></label>";
        } else if (block.type === "image") {
          body =
            '<div class="block-image-preview">' +
            (block.src
              ? '<img src="' + block.src + '" alt="">'
              : "<span>Brak obrazu</span>") +
            '</div><button type="button" class="button button--small" data-pick-image>Wybierz obraz</button>' +
            '<label>Alt<input data-field="alt" value="' +
            (block.alt || "") +
            '"></label>';
        } else {
          body =
            '<label>Tekst<textarea data-field="text" rows="3">' +
            (block.text || "") +
            "</textarea></label>";
        }

        card.innerHTML = head + '<div class="block-card__body">' + body + "</div>";
        list.appendChild(card);
      });
      sync();
    }

    list.addEventListener("input", function (event) {
      var field = event.target.getAttribute("data-field");
      if (!field) return;
      var card = event.target.closest(".block-card");
      var index = Number(card.dataset.index);
      if (field === "items") {
        blocks[index].items = event.target.value
          .split("\n")
          .map(function (line) {
            return line.trim();
          })
          .filter(Boolean);
      } else if (field === "level") {
        blocks[index].level = Number(event.target.value);
      } else {
        blocks[index][field] = event.target.value;
      }
      sync();
    });

    list.addEventListener("click", function (event) {
      var card = event.target.closest(".block-card");
      if (!card) return;
      var index = Number(card.dataset.index);
      if (event.target.matches("[data-remove]")) {
        blocks.splice(index, 1);
        render();
      } else if (event.target.matches("[data-up]") && index > 0) {
        var prev = blocks[index - 1];
        blocks[index - 1] = blocks[index];
        blocks[index] = prev;
        render();
      } else if (event.target.matches("[data-down]") && index < blocks.length - 1) {
        var next = blocks[index + 1];
        blocks[index + 1] = blocks[index];
        blocks[index] = next;
        render();
      } else if (event.target.matches("[data-pick-image]")) {
        openMediaPicker(function (item) {
          blocks[index].src = item.url;
          if (!blocks[index].alt) blocks[index].alt = item.alt_text || "";
          render();
        });
      }
    });

    root.querySelectorAll("[data-add-block]").forEach(function (button) {
      button.addEventListener("click", function () {
        var type = button.getAttribute("data-add-block");
        var block = { type: type };
        if (type === "heading") {
          block.level = 2;
          block.text = "";
        } else if (type === "list") {
          block.items = [];
        } else if (type === "image") {
          block.src = "";
          block.alt = "";
        } else {
          block.text = "";
        }
        blocks.push(block);
        render();
      });
    });

    var form = root.closest("form");
    if (form) {
      form.addEventListener("submit", function () {
        sync();
      });
    }

    render();
  }

  function initGalleryEditor(root) {
    var input = root.querySelector('input[name="gallery_json"], textarea[name="gallery_json"]');
    var list = root.querySelector("[data-gallery]");
    if (!input || !list) return;
    var items = parseJson(input.value || "[]", []);
    if (!Array.isArray(items)) items = [];

    function sync() {
      input.value = JSON.stringify(items);
    }

    function render() {
      list.innerHTML = "";
      items.forEach(function (item, index) {
        var card = document.createElement("article");
        card.className = "gallery-card";
        card.innerHTML =
          '<img src="' +
          (item.src || "") +
          '" alt="">' +
          '<label>Alt<input data-alt value="' +
          (item.alt || "") +
          '"></label>' +
          '<div class="gallery-card__actions">' +
          '<button type="button" data-up>↑</button>' +
          '<button type="button" data-down>↓</button>' +
          '<button type="button" data-remove>×</button>' +
          "</div>";
        card.dataset.index = String(index);
        list.appendChild(card);
      });
      sync();
    }

    list.addEventListener("input", function (event) {
      if (!event.target.matches("[data-alt]")) return;
      var index = Number(event.target.closest(".gallery-card").dataset.index);
      items[index].alt = event.target.value;
      sync();
    });

    list.addEventListener("click", function (event) {
      var card = event.target.closest(".gallery-card");
      if (!card) return;
      var index = Number(card.dataset.index);
      if (event.target.matches("[data-remove]")) {
        items.splice(index, 1);
        render();
      } else if (event.target.matches("[data-up]") && index > 0) {
        var prev = items[index - 1];
        items[index - 1] = items[index];
        items[index] = prev;
        render();
      } else if (event.target.matches("[data-down]") && index < items.length - 1) {
        var next = items[index + 1];
        items[index + 1] = items[index];
        items[index] = next;
        render();
      }
    });

    var addBtn = root.querySelector("[data-add-gallery]");
    if (addBtn) {
      addBtn.addEventListener("click", function () {
        openMediaPicker(function (item) {
          items.push({ src: item.url, alt: item.alt_text || "" });
          render();
        });
      });
    }

    var form = root.closest("form");
    if (form) {
      form.addEventListener("submit", function () {
        sync();
      });
    }

    render();
  }

  function initResultsEditor(root) {
    var input = root.querySelector('textarea[name="results_json"], input[name="results_json"]');
    var list = root.querySelector("[data-results]");
    if (!input || !list) return;
    var items = parseJson(input.value || "[]", []);
    if (!Array.isArray(items)) items = [];

    function sync() {
      input.value = JSON.stringify(items);
    }

    function render() {
      list.innerHTML = "";
      items.forEach(function (item, index) {
        var card = document.createElement("article");
        card.className = "gallery-card results-card";
        card.dataset.index = String(index);
        card.innerHTML =
          '<label>Etykieta<input data-label value="' +
          (item.label || "") +
          '"></label>' +
          '<label>Wartość<input data-value value="' +
          (item.value || "") +
          '"></label>' +
          '<div class="gallery-card__actions">' +
          '<button type="button" data-up>↑</button>' +
          '<button type="button" data-down>↓</button>' +
          '<button type="button" data-remove>×</button>' +
          "</div>";
        list.appendChild(card);
      });
      sync();
    }

    list.addEventListener("input", function (event) {
      var card = event.target.closest(".results-card");
      if (!card) return;
      var index = Number(card.dataset.index);
      if (event.target.matches("[data-label]")) items[index].label = event.target.value;
      if (event.target.matches("[data-value]")) items[index].value = event.target.value;
      sync();
    });

    list.addEventListener("click", function (event) {
      var card = event.target.closest(".results-card");
      if (!card) return;
      var index = Number(card.dataset.index);
      if (event.target.matches("[data-remove]")) {
        items.splice(index, 1);
        render();
      } else if (event.target.matches("[data-up]") && index > 0) {
        var prev = items[index - 1];
        items[index - 1] = items[index];
        items[index] = prev;
        render();
      } else if (event.target.matches("[data-down]") && index < items.length - 1) {
        var next = items[index + 1];
        items[index + 1] = items[index];
        items[index] = next;
        render();
      }
    });

    var addBtn = root.querySelector("[data-add-result]");
    if (addBtn) {
      addBtn.addEventListener("click", function () {
        items.push({ label: "", value: "" });
        render();
      });
    }

    var form = root.closest("form");
    if (form) {
      form.addEventListener("submit", function () {
        sync();
      });
    }

    render();
  }

  function initCoverPicker(root) {
    var input = root.querySelector('input[name="cover_image_id"]');
    var preview = root.querySelector("[data-cover-preview]");
    var clearBtn = root.querySelector("[data-cover-clear]");
    var pickBtn = root.querySelector("[data-cover-pick]");
    if (!input || !pickBtn) return;

    function setPreview(url) {
      if (!preview) return;
      preview.innerHTML = url
        ? '<img src="' + url + '" alt="Okładka">'
        : "<span>Brak okładki</span>";
    }

    pickBtn.addEventListener("click", function () {
      openMediaPicker(function (item) {
        input.value = item.id;
        setPreview(item.url);
      });
    });

    if (clearBtn) {
      clearBtn.addEventListener("click", function () {
        input.value = "";
        setPreview("");
      });
    }
  }

  function initDashboardDelete() {
    document.addEventListener("click", function (event) {
      var pageBtn = event.target.closest("[data-delete-page]");
      if (pageBtn) {
        if (!window.confirm("Usunąć tę stronę? Tej operacji nie można cofnąć.")) return;
        var pageId = pageBtn.getAttribute("data-delete-page");
        fetch("/api/admin/pages/" + pageId, { method: "DELETE" })
          .then(function (response) {
            if (!response.ok) throw new Error("Nie udało się usunąć strony.");
            pageBtn.closest("[data-page-id]").remove();
          })
          .catch(function (err) {
            window.alert(err.message || "Błąd usuwania");
          });
        return;
      }
      var projectBtn = event.target.closest("[data-delete-project]");
      if (projectBtn) {
        if (!window.confirm("Usunąć tę realizację? Tej operacji nie można cofnąć.")) return;
        var projectId = projectBtn.getAttribute("data-delete-project");
        fetch("/api/admin/projects/" + projectId, { method: "DELETE" })
          .then(function (response) {
            if (!response.ok) throw new Error("Nie udało się usunąć realizacji.");
            projectBtn.closest("[data-project-id]").remove();
          })
          .catch(function (err) {
            window.alert(err.message || "Błąd usuwania");
          });
        return;
      }
      var caseStudyBtn = event.target.closest("[data-delete-case-study]");
      if (caseStudyBtn) {
        if (!window.confirm("Usunąć to case study? Tej operacji nie można cofnąć.")) return;
        var caseStudyId = caseStudyBtn.getAttribute("data-delete-case-study");
        fetch("/api/admin/case-studies/" + caseStudyId, { method: "DELETE" })
          .then(function (response) {
            if (!response.ok) throw new Error("Nie udało się usunąć case study.");
            caseStudyBtn.closest("[data-case-study-id]").remove();
          })
          .catch(function (err) {
            window.alert(err.message || "Błąd usuwania");
          });
      }
    });
  }

  function initProjectSortable() {
    var list = document.querySelector("[data-sortable-projects]");
    if (!list || typeof Sortable === "undefined") return;
    if (!list.querySelector("[data-project-id]")) return;
    var csrf = list.getAttribute("data-csrf") || "";

    Sortable.create(list, {
      handle: ".drag-handle",
      animation: 150,
      onEnd: function () {
        var order = Array.prototype.map.call(list.querySelectorAll("[data-project-id]"), function (row) {
          return row.getAttribute("data-project-id");
        });
        fetch("/admin/projects/reorder", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ csrf_token: csrf, order: order }),
        }).catch(function () {
          window.alert("Nie udało się zapisać kolejności.");
        });
      },
    });
  }

  function initMediaUpload() {
    var form = document.querySelector("[data-media-upload]");
    var grid = document.querySelector("[data-media-grid]");
    if (!form || !grid) return;

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var data = new FormData(form);
      fetch("/api/admin/media", { method: "POST", body: data })
        .then(function (response) {
          if (!response.ok) throw new Error("Upload nieudany");
          return response.json();
        })
        .then(function (item) {
          var card = document.createElement("article");
          card.className = "media-card";
          card.setAttribute("data-media-id", String(item.id));
          card.innerHTML =
            '<img src="' +
            item.url +
            '" alt="">' +
            "<div><strong>" +
            (item.alt_text || "plik") +
            "</strong><small>" +
            item.url +
            '</small><button type="button" class="button button--small" data-copy="' +
            item.url +
            '">Kopiuj URL</button>' +
            '<button type="button" class="button button--small button--danger" data-delete-media="' +
            item.id +
            '">Usuń</button></div>';
          grid.prepend(card);
          form.reset();
          addMediaItemToPageStore({
            id: String(item.id),
            url: item.url,
            file_name: item.alt_text || "plik",
            alt_text: item.alt_text || "",
          });
        })
        .catch(function (err) {
          window.alert(err.message || "Błąd uploadu");
        });
    });

    grid.addEventListener("click", function (event) {
      var copyBtn = event.target.closest("[data-copy]");
      if (copyBtn) {
        navigator.clipboard.writeText(copyBtn.getAttribute("data-copy") || "");
        copyBtn.textContent = "Skopiowano";
        setTimeout(function () {
          copyBtn.textContent = "Kopiuj URL";
        }, 1200);
        return;
      }
      var deleteBtn = event.target.closest("[data-delete-media]");
      if (deleteBtn) {
        if (!window.confirm("Usunąć ten plik? Zniknie też ze wszystkich miejsc, w których jest użyty jako okładka.")) return;
        var mediaId = deleteBtn.getAttribute("data-delete-media");
        fetch("/api/admin/media/" + mediaId, { method: "DELETE" })
          .then(function (response) {
            if (!response.ok) throw new Error("Nie udało się usunąć pliku.");
            deleteBtn.closest("[data-media-id]").remove();
          })
          .catch(function (err) {
            window.alert(err.message || "Błąd usuwania");
          });
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-block-editor]").forEach(initBlockEditor);
    document.querySelectorAll("[data-gallery-editor]").forEach(initGalleryEditor);
    document.querySelectorAll("[data-results-editor]").forEach(initResultsEditor);
    document.querySelectorAll("[data-cover-editor]").forEach(initCoverPicker);
    initProjectSortable();
    initMediaUpload();
    initDashboardDelete();
  });
})();
