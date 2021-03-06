#Odoo repository for modules developed by Jordi Llinares

##CONTENTS

###crm_unique_email
A simple module that warns you when you try to create a new CRM lead with an email that already exists.

###float_field_color
This module extends the float field widget creating two new widgets: 'float_color' and 'float_color_inverted',
which automatically set the font color accoding to the float value sign.

USAGE: declare a float field with widget='float_color' to display positive values in green color and negative
ones in red, or with 'float_color_inverted' to invert the color rule.

###float_time_hms
Replaces the format of the 'float_time' widget, which is hh:mm, by hh:mm:ss, as there are some industries on which
some processes/operations are as short as a few seconds. This fact is specially relevant when measuring cycle
times in manufacturing.

###footer_discount
This module:

-   Adds two default discount fields to the partner form: sale and purchase discount.

-   Adds two discount fields (partner discount and additional discount) to the footer
    of each sale/purchase document (i.e. order and invoice).

-   For each new document, picks the default partner discount from the partner form.

-   Propagates footer discounts from purchase/sales orders to invoice, be it generated
    from the order itself or from a picking.

-   Propagates footer discounts from original invoice to refund.

-   Keeps into account these discounts on financial moves and payment terms generation.

Discount fields added by this module can be hidden by disabling their corresponding checkbox on both sale and
purchase configuration settings. Changes on these two checkboxes are linked to ir_config_param values, so when
you uncheck the boxes the discount fields on purchase/sale documents are not shown, and default value for the
partner discount field on each new document is set to 0 (without using these parameters, you would be able to 
hide the discount fields on new documents, but partner discount field would still be defaulted to the partner's
form 'default discount' value).

###l10n_es_cnae_2009
Adds a new entity to manage the list of economic activities defined in CNAE 2009, which is a version of european NACE.
Warning: Although module fields and views are defined both in english and spanish, master data of the CNAE list
are only in spanish.

###mrp_manual
Implements some changes on the base 'mrp' module of Odoo:
    
-   Invalidates default production wizard and, more specifically, 'action_produce'. We won't
    'consume' or 'consume and produce' anymore. Instead, consume and produce operations are
    independent and manual: 
        -   For each 'to consume' move a button and a wizard is shown. Small changes over the
            original.
        -   For each 'to produce' move, a button and a wizard is shown. A new wizard
            'stock.move.produce' is developed and linked through a button each 'to produce' move.
            This wizard works the same way that stock.move.consume, allowing to manually enter
            each production batch. A lot number can easily be generated by pressing a button from
            within the wizard, for products with production tracking enabled and lot creation
            mode set to 'auto'.
        -   The order's 'Produce' button is replaced by a 'Close order' button that warns
            you if the order has any pending consumption/production moves (it lets you close
            the order, though).
    When you have consumed/produced all you needed to, you'll 'Close order'. If there are any
    pending moves, a warning is raised (though it lets you close the order). Counterpart of this
    warning is that the page header now uses double height.

-   'Consumed' and 'Produced' fields are not showing cancelled moves anymore.

-   Displays the real produced quantity of order's product on the order form header, below the ordered
    quantity.
    
###multi_m2o_text_widget
This module is a prototype of a new field type + widget that links a field in a model with several records of
other different models. It is useful, for example when you want to track a raw material lot usage. A given lot
may have been partially served to a customer (if you sell the product) and partially consumed in a manufacturing order.

By now, you must manually take care of writing the field value: it basically consists of a text field, which content
must be a semicolon-separated list of pairs (model_name,res_id). So field value would be something like
"model_name1,res_id1;model_name2,res_id2;".

A custom widget 'multi_reference' (bad name, in fact it extends FieldMany2One widget) formats foretold data structure,
displaying it as a set of links to records of different models. You can see a working example on my 'stock_lot_enh_base'
module. Please notice that this is working properly on form view, but not on list  view or hyerarchical tree view, due
to my limited knowledge of JS/JQuery.

###stock_barcode_sound
This module adds two little improvements to the processing of picking lines through the JS barcode interface:

-   When a barcode is scanned, the interface window is scrolled to show the
    scanned element as the first one. That's specially useful if your picking
    has a lot of lines.

-   When a barcode is scanned and processed a different sound is played
    depending on if the barcode has been found or not.

###stock_lot_enh_base
Adds some features to lot management in Odoo:

-   Adds the possibility to specify a sequence for a product's lot, be it a received
    product or a manufactured product.

-   Adds a button in the 'transfer details wizard' that allows to create a new lot number
    on the fly without needing to open a new popup. Please note it only works when product's lot
    creation mode is set to 'auto' and product tracking is enabled any of these three ways: incoming,
    outgoing or all. Furthermore, button visibility is determined by a calculated boolean technical
    field: 'allows_quick_lot_creating', which is only true when transfer action is linked to an
    incoming picking.
    If a sequence has not been specified for the product and it has creation mode set to 'auto', a
    new lot number is created based on the default 'stock.lot.serial' sequence.
    
-    Adds two new char fields to production lot, aimed to give useful information on lots traceability:
    -   _origin:_ this field is automatically filled when a new lot is created, i.e. on product receival
        or manufacturing (the latter is implemented in 'stock_lot_enh_mrp' module). It shows a unique
        reference for the name of the incoming picking or manufacturing order.
    -   _destination:_ this field is automatically filled each time a given lot is moved on a picking
        of type internal or outgoing ('stock_lot_enh_mrp' writes also here the name of the manufacturing
        order when a raw material lot is consumed).
    Please note that 'origin' references an unique record, while 'destination' can contain references to
    multiple records of different models. #TODO: Develop a 'multi_many2many_list' field type and widget
    that allows to show links to different records from different models from inside a single labels-type
    field. That would greatly improve traceability UX!
    
-   'quants_get_order' implements an extra check for FEFO quants: if a quant has already expired
    (removal_date < current date), it is taken out from quants calculation. Besides, if the method
    receives 'chatter_model' and 'chatter_id' in the context, it tries to notify the situation via the
    chatter_model message thread (provided the model inherits from mail.thread).
    NOTE: This module does not depend of 'product_expiry', which implements FEFO strategy, because only
    the variable 'orderby' used by the different removal strategies is checked. We assume 'orderby'
    clause for a given strategy will always represent the same condition.
    
-   Lots tree view now has an 'Available' filter that excludes not used lot numbers. Maybe in further
    versions this filter also excludes lots without at least one quant with qty > 0 (hide lots with
    exhausted stocks).
    
WARNING: Please note that stock.quant's '_quants_get_order' method is fully overwritten, not inherited.

###stock_lot_enh_mrp
Adds some features to lot management, specifically linked to MRP:

-   Writes manufacturing order number into origin/destination fields of production lots
    when they are consumed/produced. Both fields are defined in 'stock_lot_enh_base' module.
     
-   When the 'Check availability' button of a manufacturing order form view is clicked,
    it sends context values 'chatter_model' and 'chatter_id' to custom _quants_get_order
    That method of 'stock_lot_enh_base' module ignores FEFO lots that have already expired.
    Here, thanks to the button context, it can be documented in the manufacturing order message
    thread, to inform the fact that an expired lot has been removed from available lots.
