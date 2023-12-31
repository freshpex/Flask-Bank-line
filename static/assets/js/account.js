function toggleBalance(button) {
    var targetId = button.getAttribute("data-target");
    var target = document.getElementById(targetId);
    if (target.style.display === "none") {
      target.style.display = "inline";
      // Change the eye icon to open
      button.innerHTML = "<i class='fa fa-eye'></i>";
    } else {
      target.style.display = "none";
      // Change the eye icon to closed
      button.innerHTML = "<i class='fa fa-eye-slash'></i>";
    }
  }