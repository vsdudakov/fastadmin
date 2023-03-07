/*
================================================================
* Template:  	 iDocs - One Page Documentation HTML Template
* Written by: 	 Harnish Design - (http://www.harnishdesign.net)
* Description:   Main Custom Script File
================================================================
*/

(function ($) {
  "use strict";

  // Preloader
  $(window).on("load", function () {
    $(".lds-ellipsis").fadeOut(); // will first fade out the loading animation
    $(".preloader").delay(100).fadeOut("slow"); // will fade out the white DIV that covers the website.
    $("body").delay(100);
  });

  /*-------------------------------
    Primary Menu
--------------------------------- */

  // Mobile Collapse Nav
  $(
    '.primary-menu .navbar-nav .dropdown-toggle[href="#"], .primary-menu .dropdown-toggle[href!="#"] .arrow'
  ).on("click", function (e) {
    if ($(window).width() < 991) {
      e.preventDefault();
      var $parentli = $(this).closest("li");
      $parentli.siblings("li").find(".dropdown-menu:visible").slideUp();
      $parentli.find("> .dropdown-menu").stop().slideToggle();
      $parentli.siblings("li").find("a .arrow.show").toggleClass("show");
      $parentli.find("> a .arrow").toggleClass("show");
    }
  });

  // Mobile Menu
  $(".navbar-toggler").on("click", function () {
    $(this).toggleClass("show");
  });

  /*------------------------
   Side Navigation
-------------------------- */

  $("#sidebarCollapse").on("click", function () {
    $("#sidebarCollapse span:nth-child(3)").toggleClass("w-50");
    $(".app-navigation").toggleClass("active");
  });

  /*------------------------
   Sections Scroll
-------------------------- */

  $(".app-navigation a").on("click", function () {
    event.preventDefault();
    var sectionTo = $(this).attr("href");
    $("html, body")
      .stop()
      .animate(
        {
          scrollTop: $(sectionTo).offset().top - 120,
        },
        200,
      );
  });

  /*------------------------
   Highlight Js
-------------------------- */

  hljs.initHighlightingOnLoad();

  /*------------------------
   Scroll to top
-------------------------- */
  $(function () {
    $(window).on("scroll", function () {
      if ($(this).scrollTop() > 400) {
        $("#back-to-top").fadeIn();
      } else {
        $("#back-to-top").fadeOut();
      }
    });
  });
  $("#back-to-top").on("click", function () {
    $("html, body").animate({ scrollTop: 0 });
    return false;
  });
})(jQuery);
