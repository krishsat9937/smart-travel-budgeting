interface CustomButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    name: string;
    variant?: 'primary' | 'secondary';
  }
  
  const CustomButton = ({ name, variant = 'primary', ...props }: CustomButtonProps) => {
    const baseStyles = 'px-4 py-2 rounded-md text-white font-medium focus:outline-none';
    const variantStyles =
      variant === 'primary'
        ? 'bg-blue-600 hover:bg-blue-700 focus:ring-2 focus:ring-blue-500'
        : 'bg-gray-600 hover:bg-gray-700 focus:ring-2 focus:ring-gray-500';
  
    return (
      <button className={`${baseStyles} ${variantStyles}`} {...props}>
        {name}
      </button>
    );
  };
  
  export default CustomButton;
  