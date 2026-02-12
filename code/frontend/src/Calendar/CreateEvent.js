import AxiosInstance from "./AxiosInstance"

const createEvent = () => {

    function handleChange(e){

    }
    return (
        <form>
            <label>Enter event details:
                <input type="text" value={title} onChange={handleChange}/>

            </label>
        </form>
    )
} 
export default createEvent