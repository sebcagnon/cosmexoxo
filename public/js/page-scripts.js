$('ul.dropdown-menu [data-toggle=dropdown]').on('click mouseenter',
                                                function openMenu (event) {
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

$(".addToCart").submit(function addToCart (e) {
    e.preventDefault(); // Prevents the page from refreshing
    var $this = $(this); // `this` refers to the current form element
    $.post(
        $this.attr("action"), // Gets the URL to sent the post to
        $this.serialize(), // Serializes form data in standard format
        function(data) {
          $("#cartSize").text(data.cartSize + ' item(s)');
        },
        "json" // The format the response should be in "json"
    );
});