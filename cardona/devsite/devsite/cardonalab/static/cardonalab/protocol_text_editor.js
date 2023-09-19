tinymce.init({
    selector: '#id_body',
    width: 1200,
    height: 800,
    plugins: 'lists advlist table link image charmap fullscreen',
    menubar: 'edit format insert table',
    toolbar: 'fullscreen | undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | outdent indent | numlist bullist | link image charmap',
    content_css: '/static/admin/css/base.css',
    link_title: false,
    image_caption: true
});