const Spinner = ({ loading }) => {
  if (loading) {
    return (
      <div className="w-6 h-6 border-4 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
    );
  }
  return null;
};

export default Spinner;
