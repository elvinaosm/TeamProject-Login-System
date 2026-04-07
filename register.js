function registerUser(name, email, password) {
    if (!name || !email || !password) {
        return "All fields are required";
    }
    if (password.length < 6) {
        return "Password must be at least 6 characters";
    }
    return "User registered successfully";
}