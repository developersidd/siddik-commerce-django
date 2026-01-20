// some scripts

$(document).ready(function () {
  // Toast
  function showToast(message, type = "success") {
    // Create toast element
    const toast = document.createElement("div");
    toast.className = `custom-toast ${type}`;

    // Set icon based on type
    const icon = type === "success" ? "✓" : "✕";

    toast.innerHTML = `
    <span class="toast-icon">${icon}</span>
    <span class="toast-message">${message}</span>
    <button class="toast-close" onclick="this.parentElement.remove()">×</button>
  `;

    // Add to page
    document.body.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
      toast.style.animation = "slideOut 0.3s ease-out";
      setTimeout(() => toast.remove(), 300);
    }, 5000);
  }

  // jquery ready start
  // jQuery code

  /* ///////////////////////////////////////

    THESE FOLLOWING SCRIPTS ONLY FOR BASIC USAGE, 
    For sliders, interactions and other

    */ ///////////////////////////////////////

  //////////////////////// Prevent closing from click inside dropdown
  $(document).on("click", ".dropdown-menu", function (e) {
    e.stopPropagation();
  });

  $(".js-check :radio").change(function () {
    var check_attr_name = $(this).attr("name");
    if ($(this).is(":checked")) {
      $("input[name=" + check_attr_name + "]")
        .closest(".js-check")
        .removeClass("active");
      $(this).closest(".js-check").addClass("active");
      // item.find('.radio').find('span').text('Add');
    } else {
      item.removeClass("active");
      // item.find('.radio').find('span').text('Unselect');
    }
  });

  $(".js-check :checkbox").change(function () {
    var check_attr_name = $(this).attr("name");
    if ($(this).is(":checked")) {
      $(this).closest(".js-check").addClass("active");
      // item.find('.radio').find('span').text('Add');
    } else {
      $(this).closest(".js-check").removeClass("active");
      // item.find('.radio').find('span').text('Unselect');
    }
  });

  // Bootstrap tooltip
  if ($('[data-toggle="tooltip"]').length > 0) {
    // check if element exists
    $('[data-toggle="tooltip"]').tooltip();
  } // end if

  // increase decrease button
  $("#button-plus").on("click", function (e) {
    e.preventDefault();
    let stock = parseInt($("#stock").text());
    console.log("🚀 ~ stock:", stock);
    let quantity = parseInt($("#quantity").val());
    console.log("🚀 ~ quantity:", quantity);
    if (quantity < stock) {
      $("#quantity").val(quantity + 1);
      console.log("increaing product quantity");
    }
  });

  $("#button-minus").on("click", function (e) {
    e.preventDefault();
    let quantity = parseInt($("#quantity").val());
    console.log("🚀 ~ quantity:", quantity);
    if (quantity > 1) {
      $("#quantity").val(quantity - 1);
      console.log("decreasing product quantity");
    }
  });
//
//  $("#add-to-cart-btn").on("click", function (e) {
//    e.preventDefault();
//    let productId = $(this).data("product-id"); // this
//    let quantity = $("#quantity").val();
//    console.log("🚀 ~ quantity:", quantity);
//    addToCart(productId, quantity);
//  });

  // Add to cart using AJAX
  function addToCart(productId, quantity) {
    const csrftoken = getCookie("csrftoken");
    // get varitions
    let size = $("input[name='size']");
    let color = $("input[name='color']");
    let selectedSize = $("input[name='size']:checked").val();

    let selectedColor = $("input[name='color']:checked").val();
    // check if size and color are available
    if (
      (size.length > 0 && !selectedSize) ||
      (color.length > 0 && !selectedColor)
    ) {
      showToast("Please select size and color.", "error");
      return;
    }
    const formData = new FormData();
    formData.append("product_id", productId);
    formData.append("quantity", quantity);
    if (selectedSize) formData.append("size", selectedSize);
    if (selectedColor) formData.append("color", selectedColor);
    fetch(`/cart/add/${productId}/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
        "X-Requested-With": "XMLHttpRequest",
      },
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("🚀 ~ quantity:", quantity);
        console.log("🚀 ~ data:", data);
        $("#quantity").val(1);
        // these are radio buttons, uncheck them
        size.prop("checked", false);
        color.prop("checked", false);
        $(".label-size").removeClass("active");
        $(".label-color").removeClass("active");
        return showToast(data.message, "success");
      })
      .catch((error) => {
        console.error("Error:", error);
        showToast("An error occurred. Please try again.", "error");
      });
  }

  // Function to get CSRF token from cookies
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // price range slider --- start ---
  const minRange = document.getElementById("min_range");
  const maxRange = document.getElementById("max_range");
  const minPrice = document.getElementById("min_price");
  const maxPrice = document.getElementById("max_price");
  const priceGap = 500;
  const storeMaxPrice = parseInt(minRange?.max) || 1000000;
  const rangeSelected = document.getElementById("rangeSelected");
  // Update visual range bar
  function updateRangeBar() {
    const minVal = parseInt(minRange?.value);
    const maxVal = parseInt(maxRange?.value);
    const rangeMax = parseInt(minRange?.max);

    const minPercent = (minVal / rangeMax) * 100;
    const maxPercent = (maxVal / rangeMax) * 100;
    if (rangeSelected) {
      rangeSelected.style.left = minPercent + "%";
      rangeSelected.style.right = 100 - maxPercent + "%";
    }
  }

  // Min range slider changed
  minRange?.addEventListener("input", function () {
    const minVal = parseInt(this.value);
    const maxVal = parseInt(maxRange?.value);

    // Check if the gap is less than priceGap then adjust
    // Example: min=6800, max=7000 → gap is only 200 (too small!)
    if (maxVal - minVal < priceGap) {
      console.log("min to close to max");
      this.value = maxVal - priceGap;
    }

    minPrice.value = this.value;
    updateRangeBar();
  });

  // Max range slider changed
  maxRange?.addEventListener("input", function () {
    const minVal = parseInt(minRange?.value);
    const maxVal = parseInt(this.value);

    if (maxVal - minVal < priceGap) {
      console.log("max t0oo close to min ");
      this.value = minVal + priceGap;
    }

    maxPrice.value = this.value;
    updateRangeBar();
  });

  // Min input changed
  minPrice?.addEventListener("input", function () {
    const minVal = parseInt(this.value) || 0;
    const maxVal = parseInt(maxPrice?.value) || storeMaxPrice;

    if (minVal < 0) {
      this.value = 0;
    } else if (minVal > storeMaxPrice) {
      this.value = storeMaxPrice;
    } else if (maxVal - minVal < priceGap) {
      this.value = maxVal - priceGap;
    }

    minRange.value = this.value;
    updateRangeBar();
  });

  // Max input changed
  maxPrice?.addEventListener("input", function () {
    const minVal = parseInt(minPrice?.value) || 0;
    const maxVal = parseInt(this.value) || storeMaxPrice;

    if (maxVal > storeMaxPrice) {
      this.value = storeMaxPrice;
    } else if (maxVal < 0) {
      this.value = 0;
    } else if (maxVal - minVal < priceGap) {
      this.value = minVal + priceGap;
    }

    maxRange.value = this.value;
    updateRangeBar();
  });
  updateRangeBar();

  // Product layout change
  $(".layout-btn").on("click", function () {
    const layout = $(this).data("layout");
    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set("layout", layout);
    window.location.href = currentUrl.toString();
  });
  // Sort by change
  $("#sort_by").on("change", function () {
    const selectedOption = $(this).val();
    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set("sort_by", selectedOption);
    window.location.href = currentUrl.toString();
  });

  // Pagination button click
  $(".page-btn").on("click", function () {
    const pageNum = $(this).data("page-num");
    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set("page", pageNum);
    window.location.href = currentUrl.toString();
  });
  let passwordInput = $("input[name='password']");
  let confirmPasswordInput = $("input[name='confirm_password']");
  // toggle password visibility
  $("#toggle-password").on("click", function () {
    const type =
      passwordInput.attr("type") === "password" ? "text" : "password";
    passwordInput.attr("type", type);
    // toggle icon
    $(this).toggleClass("fa-eye fa-eye-slash");
  });

  // toggle confirm password visibility
  $("#toggle-confirm-password").on("click", function () {
    const type =
      confirmPasswordInput.attr("type") === "password" ? "text" : "password";
    confirmPasswordInput.attr("type", type);
    // toggle icon
    $(this).toggleClass("fa-eye fa-eye-slash");
  });

  // show or hide toggle icon based on input
  passwordInput.on("input", function () {
    const toggleIcon = $("#toggle-password");
    if ($(this).val().length > 0) {
      toggleIcon.show();
    } else {
      toggleIcon.hide();
    }
  });
  confirmPasswordInput.on("input", function () {
    const toggleIcon = $("#toggle-confirm-password");
    if ($(this).val().length > 0) {
      toggleIcon.show();
    } else {
      toggleIcon.hide();
    }
  });
});
// jquery end
