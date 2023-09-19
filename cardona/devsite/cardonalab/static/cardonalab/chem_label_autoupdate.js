window.onload = function() {
    if (document.getElementById("id_name") != null) {
        document.getElementById("id_name").onkeyup = function() {
            for (var i = 0; i < this.value.length - 1; i++) {
                if (/[A-Z]|[a-z]/.test(this.value.charAt(i)) && this.value.charAt(i + 1) != '-') {
                    document.getElementById("id_label").value = this.value.charAt(i).toUpperCase();
                    break;
                }
            }
        }
    }
}
