$(document).ready(function () {
    //Contact Form handler

    var contactForm = $(".contact-form")
    var contactFormMethod = contactForm.attr("method")
    var contactFormEndPoint = contactForm.attr("action")


    contactForm.submit(function (event) {
        event.preventDefault()
        var contactFormSubmitBtn = contactForm.find("[type='submit']")
        var contactFormSubmitBtnTxt = contactFormSubmitBtn.text()
        var contactFormData = contactForm.serialize()
        displayLoadingBtn(contactFormSubmitBtn, true, "Sending")
        $.ajax({
            method: contactFormMethod,
            url: contactFormEndPoint,
            data: contactFormData,
            success: function (data) {
                contactForm[0].reset()
                $.alert({
                    title: "Success!",
                    content: data.message,
                    theme: "modern"
                })

                setTimeout(function () {
                    displayLoadingBtn(contactFormSubmitBtn, false, contactFormSubmitBtnTxt)
                }, 500)

            },
            error: function (error) {
                console.log(error.responseJSON)
                var jsonData = error.responseJSON
                var msn = ""

                $.each(jsonData, function (key, value) {
                    msn += key + ": " + value[0].message + "<br/>"
                })
                $.alert({
                    title: "Oops!",
                    content: msn,
                    theme: "modern"
                })

                setTimeout(function () {
                    displayLoadingBtn(contactFormSubmitBtn, false, contactFormSubmitBtnTxt)
                }, 500)

            }
        })
    })

    //Autosearch
    var searchForm = $(".search-form")
    var searchInput = searchForm.find("[name='q']")
    var typingTimer;
    var typingInterval = 500 //1000 = 1 seconds
    var searchBtn = searchForm.find("[type='submit']")

    searchInput.keyup(function (event) {
        clearTimeout(typingTimer)
        typingTimer = setTimeout(perfomSearch, typingInterval)
    })

    function displayLoadingBtn(btn, doSubmit, text) {
        if (doSubmit) {
            btn.addClass("disabled")
            btn.html("<i class='fa fa-spin fa-spinner'></i>" + text + "...")
        } else {
            btn.removeClass("disabled")
            btn.html(text)
        }
    }

    function perfomSearch() {
        displayLoadingBtn(searchBtn, true, "Searching")
        var query = searchInput.val()
        setTimeout(function () {
            window.location.href = '/search/?q=' + query
        }, 1000)

    }

    //Cart add products
    var productForm = $(".form-product-ajax")

    productForm.submit(function (event) {
        event.preventDefault();
        var thisForm = $(this)
        var actionEndpoint = thisForm.attr("action");
        var actionEndpoint = thisForm.attr("data-endpoint");
        var httpMethod = thisForm.attr("method");
        var formData = thisForm.serialize();

        $.ajax({
            url: actionEndpoint,
            method: httpMethod,
            data: formData,
            success: function (data) {
                var submitSpan = thisForm.find(".submit-span")
                if (!data.added) {
                    submitSpan.html("<button type='submit' class='btn btn-success'>Add to cart</button>")
                } else {
                    submitSpan.html("In cart <button type='submit' class='btn btn-link'>Remove?</button>")
                }
                var navbarCount = $(".navbar-cart-count")
                navbarCount.text(data.cartItemCount)
                if (window.location.href.indexOf("cart") != -1)
                    refreshCart()
            },
            error: function (errorData) {
                $.alert({
                    title: "Oops!",
                    content: "An error occurred!",
                    theme: "modern"
                })
            }
        })
    })

    function refreshCart() {
        var cartTable = $(".cart-table")
        var cartBody = cartTable.find(".cart-body")
        var productRows = cartBody.find(".cart-product")
        var refreshCartUrl = '/api/cart/';
        var refreshCartMethod = "GET"
        var data = {}
        $.ajax({
            url: refreshCartUrl,
            method: refreshCartMethod,
            data: data,
            success: function (data) {
                if (data.products.length > 0) {
                    var hiddenCartItemRemoveForm = $(".cart-item-remove-form")
                    productRows.html("")
                    $.each(data.products, function (index, value) {
                        var newCartItemRemove = hiddenCartItemRemoveForm.clone()
                        newCartItemRemove.css("display", "block")
                        newCartItemRemove.find(".cart-item-product-id").val(value.id)
                        cartBody.prepend("<tr><th scope=\"row\">" + (data.products.length - index) +
                            "</th><td><a href='" + value.url + "'>" + value.name + "</a>" + newCartItemRemove.html() +
                            "</td><td>" + value.price + "</td></tr>")
                        console.log(index)
                    })

                    cartBody.find(".cart-subtotal").text(data.subtotal)
                    cartBody.find(".cart-total").text(data.total)
                }
                else
                    window.location.href = window.location.href
            },
            error: function (errorData) {
                $.alert({
                    title: "Oops!",
                    content: "An error occurred!",
                    theme: "modern"
                })
            }
        })
    }
})