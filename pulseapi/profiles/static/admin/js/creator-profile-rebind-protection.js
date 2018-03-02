document.addEventListener("DOMContentLoaded", function(e) {
  var selector = document.getElementById("id_creator");
  selector.addEventListener("change", function(e) {
    result = window.confirm(
      "Are you sure you want to change this binding?\n\n" +
      "WARNING: This change CANNOT be undone. If you set this to a creator that is already associated with another profile, that profile will lose its association to the selected creator and all entries that referenced that creator will now link to this profile."
    );

    if (!result) {
      e.preventDefault();
    }
  });
});
