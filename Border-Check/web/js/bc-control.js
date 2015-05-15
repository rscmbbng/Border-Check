var BcControlClass = L.Control.extend({
    options: {
        position: 'bottomright'
    },

    onAdd: function (map) {
        // create the control container with a particular class name
        var container = L.DomUtil.create('div', 'bc-custom-control');
        // ... initialize other DOM elements, add listeners, etc.

        return container;
    }
});

var bcControl = new BcControlClass();
