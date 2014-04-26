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