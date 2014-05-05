// special dropdown menu that overrides default bootstrap behavior
$('ul.dropdown-menu [data-toggle=dropdown]')
  .on('click mouseenter', function openMenu (event) {
  // Avoid following the href location when clicking
  event.preventDefault();
  // Avoid having the menu to close when clicking
  event.stopPropagation();
  var parent = $(this).parent();
  if (event.type == 'click') {
    // If a menu is already open we close it
    if (parent.hasClass('open'))
        return parent.removeClass('open');
    parent.addClass('open');
  } else if (event.type == 'mouseenter') {
    if (!parent.hasClass('open'))
        parent.addClass('open');
  }
  if (parent.hasClass('open')) {
    parent.siblings().removeClass('open');

    // opening the one you clicked on
    parent.addClass('open');

    var menu = $(this).parent().find("ul");
    var menupos = menu.offset();

    if ((menupos.left + menu.width()) + 30 > $(window).width()) {
    var newpos = - menu.width() + 5;
    } else {
    var newpos = parent.width() - 5;
    }
    menu.css({ left:newpos });
  }
});

// allows to add and remove from cart without refreshing the current page
$(".no-refresh").submit(function changeCart (e) {
    e.preventDefault(); // Prevents the page from refreshing
    var $this = $(this); // `this` refers to the current form element
    var btn = $this.children(":submit");
    btn.addClass("active disabled");
    btn.after('<img id="loadImg" src="/images/ajax-loader.gif" alt="loading">');
    $.post(
        $this.attr("action"), // Gets the URL to send the post to
        $this.serialize(), // Serializes form data in standard format
        function(data) {
          if (data.error)
            return console.log('request returned an error: ' + data.error);
          $(".cartSize").text(data.cartSize);
          if (btn.hasClass("btn-primary")) {
            btn.removeClass("btn-primary active disabled")
              .addClass("btn-success").attr("value", "Added");
          } else if (btn.hasClass("btn-danger")) {
            btn.removeClass("btn-danger active, disabled")
              .addClass("btn-warning").attr("value", "Removed");
            var rowID = '#' + $this.children(':input[name=variant_id]').attr("value");
            $(rowID).remove();
          }
          $this.children("#loadImg").remove();
          if ($("#cartTable").length) {
            updateCart(data.cart);
          }
        },
        "json" // The format the response should be in "json"
    );
});

// Updates all the prices in the cart page when changing a quantity or product
function updateCart(cart) {
  var totalPrice = 0;
  for (var i=0; i<cart.length; i++) {
    var product = cart[i];
    var variant = product.variant;
    var vid = '#' + variant.variant_id;
    $(vid).find("#price").text(variant.price + ' $');
    $(vid).find("#quantity").text(product.quantity);
    $(vid).find("#price").text((variant.price*product.quantity) + ' $');
    totalPrice += variant.price*product.quantity;
  }
  $("#itemTotal").text(totalPrice + ' $');
  updateOrderPrice();
}

// update order price when shipping option is changed and on load
$("#shippingCost").change( updateOrderPrice ).change();

// does the #orderPrice update
function updateOrderPrice () {
  var total = parseInt($("#itemTotal").text()) +
              parseInt($("#shippingCost").val());
  $("#orderTotal").html('<h4>' + total + ' $</h4>');
}