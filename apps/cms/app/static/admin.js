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

  function openMediaPicker(onSelect) {
    var items = mediaItemsFromPage();
    var overlay = document.createElement("div");
    overlay.className = "media-picker";
    overlay.innerHTML =
      '<div class="media-picker__dialog">' +
      "<header><h3>Wybierz media</h3><button type=\"button\" class=\"link-button\" data-close>Zamknij</button></header>" +
      '<div class="media-picker__grid"></div>' +
      "</div>";
    var grid = overlay.querySelector(".media-picker__grid");
    if (!items.length) {
      grid.innerHTML = '<p class="empty">Brak plików. Prześlij media w bibliotece.</p>';
    } else {
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
    overlay.addEventListener("click", function (event) {
      if (event.target === overlay || event.target.matches("[data-close]")) {
        overlay.remove();
      }
    });
    document.body.appendChild(overlay);
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
            '">Kopiuj URL</button></div>';
          grid.prepend(card);
          form.reset();
          var store = document.getElementById("media-data");
          if (store) {
            var items = parseJson(store.textContent || "[]", []);
            items.unshift({
              id: String(item.id),
              url: item.url,
              file_name: item.alt_text || "plik",
              alt_text: item.alt_text || "",
            });
            store.textContent = JSON.stringify(items);
          }
        })
        .catch(function (err) {
          window.alert(err.message || "Błąd uploadu");
        });
    });

    grid.addEventListener("click", function (event) {
      var btn = event.target.closest("[data-copy]");
      if (!btn) return;
      navigator.clipboard.writeText(btn.getAttribute("data-copy") || "");
      btn.textContent = "Skopiowano";
      setTimeout(function () {
        btn.textContent = "Kopiuj URL";
      }, 1200);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-block-editor]").forEach(initBlockEditor);
    document.querySelectorAll("[data-gallery-editor]").forEach(initGalleryEditor);
    document.querySelectorAll("[data-cover-editor]").forEach(initCoverPicker);
    initProjectSortable();
    initMediaUpload();
  });
})();
