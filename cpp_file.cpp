int main()
{
    int var1;
    int miVariable = 0;

    std::cout << "456Hello, World 02 !" << std::endl;
    std::cin >> miVariable;
    std::cout << "Hola";
    std::cin >> var1 >> var2;
    
    if (var1 == 0)
    {
        std::cout << "Variable is zero" << std::endl;
    }
    else
    {
        std::cout << "Variable is not zero" << std::endl;
    }

    var1 = 0;

    while(var1 < 10)
    {
        std::cout << "Variable is less than 10" << std::endl;
        var1 = var1 + 1;
    }

    return 0;
}