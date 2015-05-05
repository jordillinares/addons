openerp.float_field_color = function(instance){

    // Form view widget
	instance.web.form.FieldFloatColor = instance.web.form.FieldFloat.extend({

        format_value: function(val, def) {
            return instance.web.format_value(val, {type: "float", digits: (this.node.attrs || {}).digits || this.field.digits}, def);
        },

	    render_value: function() {
            if (!this.get("effective_readonly")) {
                this._super();
            } else {
                var color = '';
                if (this.get('value') >= 0.0) {
                    color = 'green';
                } else {
                    color = 'red';
                }
                this.$el.find('.oe_form_char_content').css('color', color);
                var show_value = this.format_value(this.get('value'), '');
                this.$(".oe_form_char_content").text(show_value);
            }
        },

	});

	instance.web.form.widgets.add('float_color', 'instance.web.form.FieldFloatColor');


	instance.web.form.FieldFloatColorInverted = instance.web.form.FieldFloatColor.extend({

	    render_value: function() {
            if (!this.get("effective_readonly")) {
                this._super();
            } else {
                var color = '';
                if (this.get('value') <= 0.0) {
                    color = 'green';
                } else {
                    color = 'red';
                }
                this.$el.find('.oe_form_char_content').css('color', color);
                var show_value = this.format_value(this.get('value'), '');
                this.$(".oe_form_char_content").text(show_value);
            }
        },

	});

	instance.web.form.widgets.add('float_color_inverted', 'instance.web.form.FieldFloatColorInverted');

}